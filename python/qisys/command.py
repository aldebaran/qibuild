#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" This module contains few functions around subprocess """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import signal
import threading
import platform
import contextlib
import subprocess
import six

import qibuild.config
from qisys import ui

# Cache for find_program()
_FIND_PROGRAM_CACHE = dict()
SIGINT_EVENT = threading.Event()


class Process(object):
    """
    A simple way to run commands.
    Command will be started by run according to timeout parameter (not
    specified == no timeout). If it firstly send a SIGTERM signal to the
    process and wait 5 seconds for it to terminate alone (timeout). If it
    doesn't stop by itself, it will kill the group of process (created with
    subprocess) to exterminate it. Process is then considered to be a zombie.
    You can then use Process.return_type to know the state of the process:
    Possible values:
    * Process.OK   (exit code is zero)
    * Process.FAILED (exit code is > 0)
    * Process.TIME_OUT (process timed out)
    * Process.INTERRUPTED (exit code is < 0)
    * Process.NOT_RUN (could not start the process)
    * Process.ZOMBIE (could not kill process after it timed out)
    """

    OK = 0
    FAILED = 1
    TIME_OUT = 2
    ZOMBIE = 3
    INTERRUPTED = 4
    NOT_RUN = 5

    def __init__(self, cmd, cwd=None, env=None, capture=True):
        """ Process Init """
        self.cmd = cmd
        self.cwd = cwd
        self.env = env
        self.out = ""
        self.returncode = None
        self._process = None
        self.exception = None
        self.return_type = Process.FAILED
        self.capture = capture
        self._thread = None
        self._should_stop_reading = False
        self._reading_thread = None

    def run(self, timeout=None):
        """ Run Process """
        def target():
            """ Target """
            ui.debug("Starting thread.")
            ui.debug("Calling:", subprocess.list2cmdline(self.cmd))
            try:
                opts = dict()
                if os.name == 'posix':
                    opts = {
                        'preexec_fn': os.setsid,  # pylint:disable=no-member
                        'close_fds': True
                    }
                elif os.name == 'nt':
                    opts = {
                        'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP,
                    }
                kwargs = {
                    "cwd": self.cwd,
                    "env": self.env
                }
                kwargs.update(opts)
                if self.capture:
                    kwargs["stdout"] = subprocess.PIPE
                    kwargs["stderr"] = subprocess.STDOUT
                self._process = subprocess.Popen(self.cmd, **kwargs)
            except Exception as e:
                self.exception = e
                self.return_type = Process.NOT_RUN
                return

            def read_target():
                """ Read Target """
                self.out = self._process.communicate()[0]

            self._should_stop_reading = False
            self._reading_thread = threading.Thread(target=read_target)
            # Allow Python to exit even if the reading thread is still alive
            # (i.e the process is still running even after we tried to kill it)
            self._reading_thread.daemon = True
            self._reading_thread.start()
            while not self._should_stop_reading and self._reading_thread.is_alive():
                self._reading_thread.join(1)
            self.returncode = self._process.returncode
            if self.returncode == 0:
                ui.debug("Setting return code to Process.OK")
                self.return_type = Process.OK
            ui.debug("Thread terminated.")
        self._thread = threading.Thread(target=target)
        self._thread.start()
        while ((timeout is None or timeout > 0)
               and self._thread.is_alive()
               and not SIGINT_EVENT.is_set()):
            self._thread.join(1)
            if timeout is not None:
                timeout -= 1
        if not self._thread.is_alive():
            return
        elif SIGINT_EVENT.is_set():
            self._interrupt()
        else:
            ui.debug("Process timed out")
            self._kill_subprocess()

    def _kill_subprocess(self):
        """ Kill SubProcess """
        if self._thread and self._process:
            self.return_type = Process.TIME_OUT
            ui.debug("Terminating process")
            try:
                self._process.terminate()
            except Exception:
                pass
            ui.debug("Terminating process failed")
            self._thread.join(5)
            if self._thread.is_alive():
                ui.debug("Killing zombies")
                self._destroy_zombie()

    def _interrupt(self):
        """ Interrup Process """
        if self._process and self._thread.is_alive():
            self._destroy_zombie()
        self.return_type = Process.INTERRUPTED

    def _destroy_zombie(self):
        """ Destroy Zombie """
        if not self._process:
            pass
        elif os.name == 'posix':
            os.killpg(self._process.pid, signal.SIGKILL)  # pylint:disable=no-member
        elif os.name == 'nt':
            os.kill(self._process.pid, signal.CTRL_BREAK_EVENT)  # pylint:disable=no-member
        self.return_type = Process.ZOMBIE
        self._should_stop_reading = True
        self._thread.join()


def str_from_signal(code):
    """
    Return a description about what happened when the
    retcode of a program is less than zero.
    """
    if os.name == "nt":
        # windows ret code are usually displayed
        # in hexa:
        return "0x%X" % (2 ** 32 - code)
    if code == signal.SIGSEGV:
        return "Segmentation fault"
    if code == signal.SIGABRT:
        return "Aborted"
    return "%i" % code


class CommandFailedException(Exception):
    """ Custom exception """

    def __init__(self, cmd, returncode, cwd=None, stdout=None, stderr=None):
        """ CommandFailedException Init """
        super(CommandFailedException, self).__init__()
        self.cmd = cmd
        self.cwd = cwd
        if cwd is None:
            self.cwd = os.getcwd()
        self.returncode = returncode
        self.stdout = stdout
        if stdout is None:
            self.stdout = ""
        self.stderr = stderr
        if stderr is None:
            self.stderr = ""

    def __str__(self):
        """ CommandFailedException String Representation """
        mess = """The following command failed\n{cmd}\nReturn code is {returncode}\nWorking dir was {cwd}\n"""
        mess = mess.format(cmd=self.cmd, returncode=self.returncode, cwd=self.cwd)
        if self.stdout:
            mess += "Stdout: \n"
            mess = "\n".join("    " + line for line in self.stdout.split("\n"))
        if self.stderr:
            mess += "Stderr: \n"
            mess = "\n".join("    " + line for line in self.stderr.split("\n"))
        return mess


class ProcessCrashedError(Exception):
    """ An other custom exception, used by call_background """

    def __init__(self, cmd):
        """ ProcessCrashedError Init """
        super(ProcessCrashedError, self).__init__()
        self.cmd = cmd

    def __str__(self):
        """ ProcessCrashedError String Representation """
        return "%s crashed!\nFull command: %s" % (os.path.basename(self.cmd[0]), self.cmd)


class NotInPath(Exception):
    """ Custom exception """

    def __init__(self, executable, env=None):
        """ NotInPath Init """
        super(NotInPath, self).__init__()
        self.executable = executable
        self.env = env

    def __str__(self):
        """ NotInPath String Representation """
        if self.env:
            path_env = self.env.get("PATH")
        else:
            path_env = os.environ["PATH"]
        return "Could not find executable: %s\nLooked in:\n%s" % (
            self.executable,
            "\n".join(path_env.split(os.pathsep))
        )


def get_toolchain_binary_paths(build_config):
    """ Get the toolchain of the build_config and return the PATH of every bin packages as a string """
    bins = []
    if build_config:
        toolchain = None
        try:
            if hasattr(build_config, 'toolchain'):
                toolchain = build_config.toolchain
            else:
                # When called from qibuildfarm.release.functions (ie: build_config is the build_config name as string)
                from qibuild.config import QiBuildConfig
                from qitoolchain import get_toolchain
                qibuild_cfg = QiBuildConfig()
                qibuild_cfg.read()
                qibuild_config = qibuild_cfg.configs.get(build_config)
                if qibuild_config:
                    toolchain = get_toolchain(qibuild_config.toolchain)
            if toolchain:
                for pkg in toolchain.packages:
                    bin_dir = os.path.join(pkg.path, 'bin')
                    if os.path.isdir(bin_dir):
                        bins.append(bin_dir)
        except Exception:
            pass
    return os.pathsep.join(bins)


def find_program(executable, env=None, raises=False, build_config=None):
    """
    Get the full path of an executable by
    looking at PATH environment variable
    (and PATHEXT on windows)
    Toolchain binaries from build_config are also prepend to path.
    :return: None if program was not found,
      the full path to executable otherwise
    """
    if executable in _FIND_PROGRAM_CACHE:
        return _FIND_PROGRAM_CACHE[executable]
    res = None
    if not env:
        env = dict(qibuild.config.get_build_env())
        if not env:
            env = dict(os.environ)
    toolchain_paths = get_toolchain_binary_paths(build_config)
    if toolchain_paths:
        env["PATH"] = os.pathsep.join((toolchain_paths, env.get("PATH", "")))
    for path in env["PATH"].split(os.pathsep):
        res = _find_program_in_path(executable, path)
        if res and _is_runnable(res):
            ui.debug("Use %s from: %s" % (executable, res))
            _FIND_PROGRAM_CACHE[executable] = res
            return res
    if raises:
        raise NotInPath(executable, env=env)
    return None


def _find_program_in_path_win(executable, path):
    """ Find Prograp In Path for Windows """
    path_ext = os.environ["PATHEXT"]
    extensions = path_ext.split(";")
    extensions = [x.lower() for x in extensions]
    extensions.append("")
    for ext in extensions:
        candidate = executable + ext
        res = _check_access(candidate, path)
        if res:
            return res
    return None


def _find_program_in_path(executable, path):
    """ Find Program In Path """
    if os.name == 'nt':
        return _find_program_in_path_win(executable, path)
    return _check_access(executable, path)


def _check_access(executable, path):
    """ Check Access """
    full_path = os.path.join(path, executable)
    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
        return full_path
    return None


def _is_runnable(full_path):
    """
    Return True if executable:
    - has the same architecture (32/64 bits) than current python executable
    - on linux, each dynamically linked libraries (found with 'ldd') have the minimum required version
    """
    if platform.architecture(full_path)[0] != platform.architecture(sys.executable)[0]:
        return False
    try:
        process = subprocess.Popen(['ldd', full_path], stdout=subprocess.PIPE, env={str("LANG"): str("C")})
        output = process.communicate()[0]
        if six.PY3:
            output = str(output)
        if process.returncode == 0 and ' not found ' not in output:
            return True
        elif process.returncode == 1 and 'not a dynamic executable' in output:
            return True
        return False
    except OSError:
        # TODO: Run an equivalent test on mac and on windows
        ui.warning("ldd not available => assuming {} is runnable".format(full_path))
        return True


# Implementation widely inspired by the python-2.7 one.
def check_output(*popenargs, **kwargs):
    r"""
    Run command with arguments and return its output as a byte string.
    If the exit code was non-zero it raises a CommandFailedException. The
    CommandFailedException object will have the return code in the returncode
    attribute, output in the ``stdout`` attribute and error in the ``stderr``
    attribute.
    The arguments are the same as for the Popen constructor.  Example:
    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'
    The ``stdout`` argument is not allowed as it is used internally.
    To capture standard error in the result, use ``stderr=STDOUT``.
    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    ui.debug("calling", *popenargs)
    cwd = kwargs.get('cwd')
    if sys.version_info <= (2, 7):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, error = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CommandFailedException(cmd, retcode, cwd=cwd,
                                         stdout=output, stderr=error)
    else:
        try:
            output = subprocess.check_output(*popenargs, **kwargs)
        except subprocess.CalledProcessError as err:
            raise CommandFailedException(err.cmd, err.returncode,
                                         cwd=cwd, stdout=err.output)
    ui.debug(output)
    return output


def check_output_error(*popenargs, **kwargs):
    r"""
    Run command with arguments and return its output and error as a byte string.
    If the exit code was non-zero it raises a ``CalledProcessError``.  The
    ``CalledProcessError`` object will have the return code in the returncode
    attribute and error concatenated at the end of output in the output attribute.
    The arguments are the same as for the ``Popen`` constructor.  Examples:
    >>> check_output_error(["tar", "tf", "foo.tbz2"])
    ('./\n./usr/\n./usr/bin/\n./usr/bin/foo\n',
    '\nbzip2: (stdin): trailing garbage after EOF ignored\n')
    >>> try:
    ...     qisys.command.check_output_error(['tar', '--bzip2', '-tf', 'foo.tar.gz'])
    ... except subprocess.CalledProcessError as e:
    ...     print(e)
    The following command failed
    ['tar', '--bzip2', '-tf', 'foo.tar.gz']
    Return code is 2
    Working dir was /tmp
    Stdout:
        <nothing>
    Stderr:
        bzip2: (stdin) is not a bzip2 file.
        tar: Child returned status 2
        tar: Error is not recoverable: exiting now
    The ``stdout`` and ``stderr`` arguments are not allowed as they are used internally.
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    if 'stderr' in kwargs:
        raise ValueError('stderr argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, stderr=subprocess.PIPE, *popenargs, **kwargs)
    output, error = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CommandFailedException(cmd, retcode, stdout=output, stderr=error)
    return output, error


def check_is_in_path(executable, env=None):
    """ Check that the given executable is to be found in %PATH% """
    if find_program(executable, env=env) is None:
        raise NotInPath(executable, env=env)


def call(cmd, cwd=None, env=None, ignore_ret_code=False, quiet=False):
    """
    Execute a command line.
    If ignore_ret_code is False:
        raise CommandFailedException if returncode is None.
    Else:
        simply returns the returncode of the process
    Note: first arg of the cmd is assumed to be something
    inside %PATH%. (or in env[PATH] if env is not None)
    Note: the shell= argument of the subprocess.Popen
    call will always be False.
    can raise:
      * CommandFailedException if ignore_ret_code is False
        and returncode is non zero
      * NotInPath  if first arg of cmd is not in %PATH%
      * And a normal exception if cwd is given and is not
        an existing directory.
    """
    exe_full_path = find_program(cmd[0], env=env)
    if not exe_full_path:
        raise NotInPath(cmd[0], env=env)
    cmd[0] = exe_full_path
    if cwd:
        if not os.path.exists(cwd):
            # We know we are likely to have a problem on windows here,
            # so always raise.
            raise Exception("Trying to run %s in non-existing %s" %
                            (" ".join(cmd), cwd))
    ui.debug("Calling:", " ".join(cmd))
    if env:
        env = dict(((str(key), str(val)) for key, val in env.items()))
    call_kwargs = {"env": env, "cwd": cwd}
    if quiet or ui.CONFIG.get("quiet"):
        call_kwargs["stdout"] = subprocess.PIPE
    returncode = subprocess.call(cmd, **call_kwargs)
    if returncode != 0 and not ignore_ret_code:
        raise CommandFailedException(cmd, returncode, cwd)
    return returncode


@contextlib.contextmanager
def call_background(cmd, cwd=None, env=None):
    """
    To be used in a "with" statement::
        with call_background(...):
           do_stuff()
        do_other_stuff()
    Process is run in the background, then do_stuff() is called.
    By the time you are executing do_other_stuff(),
    you know that the process has been killed,
    better yet, if an exception has occurred during
    do_stuff, this exception is re-raised *after*
    the process has been killed.
    """
    process = subprocess.Popen(cmd, cwd=cwd, env=env)
    caught_error = None
    try:
        yield
    except Exception as err:
        caught_error = err
    finally:
        try:
            if process.poll() is not None:
                # Process should not have died !
                raise ProcessCrashedError(cmd)
            else:
                process.kill()
        except ProcessCrashedError as err:
            caught_error = err
    if caught_error:
        raise caught_error  # pylint:disable=raising-bad-type
