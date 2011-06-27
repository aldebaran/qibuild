## Copyright (C) 2011 Aldebaran Robotics
""" This modules contains few functions around subprocess


Few notes:

 - for each command, we try to look the executable in PATH,
 (also using %PATHEXT% on windows), raising a NotInPath exception when
 not found.

 This way:
     We can alway use:
        - qibuild.command.check_call(["cmake", ..."])
    on every platform as soon as cmake is in
    os.environ["PATH"]

    without:
       - using shell=True
        (although we can display it in our error message)
       - caring about the fact that it in fact "cmake.exe" on windows:
    but:
        - still using native, absolute paths for the executables we run.
        (which is nice when debugging)

    Note that on windows, you can specify paths to add to %PATH% in
    qibuild configuration file, without polluting you whole
    environment.

 - Unless explicitly told not to, we alway raise an exception when
 the return code of the command is not zero.
     Return code always matter when you are building software ;-)

"""

import os
import sys
import contextlib
import logging
import subprocess
import threading
import Queue

from qibuild import log

LOGGER = logging.getLogger(__name__)

DRYRUN           = False

class CommandFailedException(Exception):
    """Custom exception """
    def __init__(self, cmd, returncode, cwd=None):
        self.cmd = cmd
        if cwd is None:
            self.cwd = os.getcwd()
        else:
            self.cwd = cwd
        self.returncode = returncode

    def __str__(self):
        mess  = """The following command failed
{cmd}
Return code is {returncode}
Working dir was {cwd}
"""
        return mess.format(cmd=self.cmd, returncode=self.returncode, cwd=self.cwd)


class ProcessCrashedError(Exception):
    """An other custom exception, used by call_background """
    def __init__(self, script_path):
        self.process_name = os.path.basename(script_path)

    def __str__(self):
        return "%s crashed!" % self.process_name

class NotInPath(Exception):
    """Custom exception """
    def __init__(self, executable):
        self.executable = executable

    def __str__(self):
        mess  = "Could not find executable: %s\n" % self.executable
        mess += "Looked in:\n"
        mess += "\n".join(os.environ["PATH"].split(os.pathsep))
        return mess


def find_program(executable):
    """Get the full path of an executable by
    looking at PATH environment variable
    (and PATHEXT on windows)

    return None if program was not found
    """
    full_path = None
    env_path = os.environ["PATH"]
    for path in env_path.split(os.pathsep):
        full_path = os.path.join(path, executable)
        if os.access(full_path, os.X_OK):
            return full_path
        pathext = os.environ.get("PATHEXT")
        if pathext:
            for ext in pathext.split(";"):
                with_ext = full_path + ext
                if os.access(with_ext, os.X_OK):
                    return with_ext
    return None


def check_is_in_path(executable):
    """Check that the given executable is to be found in %PATH%"""
    if find_program(executable) is None:
        raise NotInPath(executable)


def call(cmd, cwd=None, env=None, ignore_ret_code=False):
    """ Execute a command line.

    If ignore_ret_code is False:
        raise CommandFailedException if returncode is None.
    Else:
        simply returns the returncode of the process

    Note: first arg of the cmd is assumed to be something
    inside %PATH%.

    Note: the shell= argument of the subprocess.Popen
    call will always be False.

    can raise:
        - CommandFailedException if ignore_ret_code is False
        and returncode is non zero
        - NotInPath  if first arg of cmd is not in %PATH%
        - and normal exception if cwd is given and is not
        an existing directory.

    If sys.stdout or sys.stderr are not a tty, only write
    the last 300 lines of the process to sys.stdout if the
    returncode is not zero, else write everything.

    Note: this trick with sys.stderr, sys.stdout and subprocess
    does not work on windows with python < 2.7, so it is simply
    disabled, and you have a normal behavior instead.

    """
    check_is_in_path(cmd[0])
    if cwd:
        if not os.path.exists(cwd):
            raise Exception("Trying to to run %s in non-existing %s" %
                (" ".join(cmd), cwd))
    buffer = RingBuffer(300)

    returncode = 0
    minimal_write = False
    if sys.platform.startswith("win") and sys.version_info < (2, 7):
        returncode = subprocess.call(cmd, env=env, cwd=cwd)
    else:
        # This code won't work on windows with python < 2.7
        cmdline = CommandLine(cmd, cwd=cwd, env=env, shell=False)
        if not sys.stdout.isatty() or not sys.stderr.isatty():
            minimal_write = True

        for(out, err) in cmdline.execute():
            if out is not None:
                if not minimal_write:
                    sys.stdout.write(out)
                buffer.append(out)
            if err is not None:
                if not minimal_write:
                    sys.stderr.write(err)
                buffer.append(err)
        returncode = cmdline.returncode

    sys.stdout.flush()
    sys.stderr.flush()
    if ignore_ret_code:
        return returncode

    if returncode != 0:
        if minimal_write:
            lines = buffer.get()
            for line in lines:
                sys.stdout.write(line)
        # Raise correct exception
        raise CommandFailedException(cmd, returncode, cwd)


@contextlib.contextmanager
def call_background(script_path, args, environ=None):
    """
    To be used in a "with" statement.

    with call_background(...):
       do_stuff()

    do_other_stuff()

    Process is run in the background, then do_stuff()
    is called.

    By the time you are executing do_other_stuff(),
    you know that the process has been killed,
    better yet, if an exception has occurred during
    do_stuff, this exception is re-raised *after*
    the process has been killed.

    """
    cmd = [script_path] + args
    process = subprocess.Popen(cmd)
    caught_error = None
    try:
        yield
    except Exception, err:
        caught_error = err
    finally:
        try:
            if process.poll() != None:
                # Process should not have died !
                raise ProcessCrashedError(script_path)
            else:
                process.kill()
        except ProcessCrashedError, err:
            caught_error = err
    if caught_error:
    #pylint: disable-msg=E0702
    #(we are not going to raise None...)
        raise caught_error




# This CommandLine class with an .execute generator
# is a idea taken from Bitten (BSD license), thanks pals!
class CommandLine:
    """Helper for executing subprocess

    """
    def __init__(self, cmd, cwd=None, env=None, shell=False):
        self.cmd = cmd
        self.cwd = cwd
        self.env = env
        cmd_str = " ".join(cmd)

        self.returncode = None

    def execute(self):
        """Execute the command, and return a generator for iterating over
        the output written to the standard output and error streams.

        """
        def reader(pipe, pipe_name, queue):
            "To be called in a thread"
            while pipe and not pipe.closed:
                line = pipe.readline()
                if line == '':
                    break
                queue.put((pipe_name, line))
            if not pipe.closed:
                pipe.close()

        process =  subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.cwd,
            env=self.env)
        queue = Queue.Queue()

        pipe_out = threading.Thread(target=reader,
            args=(process.stdout, 'stdout', queue))
        pipe_err = threading.Thread(target=reader,
            args=(process.stderr, 'stderr', queue))

        pipe_out.start()
        pipe_err.start()

        while True:
            if process.poll() is not None and self.returncode is None:
                self.returncode = process.returncode
            try:
                name, line = queue.get(block=True, timeout=.01)
                if name == "stderr":
                    yield(None, line)
                else:
                    yield(line, None)
            except Queue.Empty:
                if self.returncode is not None:
                    break

        pipe_out.join()
        pipe_err.join()


class RingBuffer:
    """Quick'n dirty implementation of a ring buffer

    >>> rb = RingBuffer(4)
    >>> rb.append(1)
    >>> rb.get()
    [1]
    >>> rb.append(2); rb.append(3); rb.append(4)
    >>> rb.get()
    [1, 2, 3, 4]
    >>> rb.append(5)
    >>> rb.get()
    [2, 3, 4, 5]
    >>> rb.append(6)
    >>> rb.get()
    [3, 4, 5, 6]

    """
    def __init__(self, size):
        self.size = size
        self._data = list()
        self._full = False
        self._index = 0

    def append(self, x):
        if self._full:
            self._data[self._index] = x
        else:
            self._data.append(x)
            if len(self._data) == self.size:
                self._full = True
        self._index = (self._index + 1) % self.size

    def get(self):
        return self._data[self._index:] + \
               self._data[:self._index]
