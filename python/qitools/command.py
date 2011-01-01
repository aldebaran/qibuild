"""
This modules contains wrapper classes
around subprocess

"""

import subprocess
import os
from subprocess          import CalledProcessError
import logging

class CommandFailedException(Exception):
    """Custom exception """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

LOGGER = logging.getLogger("qitools.command")

DRYRUN           = False

def check_call(cmd, ignore_ret_code=False,
                    cwd=None,
                    shell=False,
                    env=None,
                    return_ret_code=False,
                    output_to_logger=False,
                    verbose_exception=False):
    """
    call a command from a working dir.
    Raise a BuildToolException if the return code
    is not zero and ignore_ret_code if False

    Warning: if output_to_logger is activated, the log will be stored in RAM

    """
    #changing the working directory is not enough.. change the env var too (or git at least will not be happy)
    if cwd:
        if not env:
            env = os.environ.copy()
        env["PWD"] = cwd
    LOGGER.debug("calling: %s", " ".join(cmd))
    if DRYRUN:
        return 0
    try:
        outputlist = list()
        if output_to_logger or verbose_exception:
            process = subprocess.Popen(cmd, cwd=cwd, env=env,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            outputlist = process.communicate()[0].split("\n")
            if output_to_logger:
                for line in outputlist:
                    LOGGER.info(line)
            retcode = process.returncode
        else:
            retcode = subprocess.call(cmd, cwd=cwd, env=env)

    except OSError as e:
        _raise_error(cmd, cwd, shell, exception=e, output=outputlist)
    except CalledProcessError as e:
        _raise_error(cmd, cwd, shell, exception=e, output=outputlist)

    if ignore_ret_code:
        return 0

    if retcode != 0:
        if return_ret_code == False:
            _raise_error(cmd, cwd, shell, retcode=retcode, output=outputlist)
    return retcode

def call(cmd, cwd=None, shell=False, env=None):
    """
    call without exception if retcode is not 0
    """
    return check_call(cmd, ignore_ret_code=True, shell=shell, cwd=cwd, env=env)

def call_retcode(cmd, cwd=None, shell=False, env=None):
    """
    call which returns the true return code
    """
    return check_call(cmd, shell=shell, cwd=cwd, env=env, return_ret_code=True)

def call_output(cmd, cwd=None, shell=False, env=None):
    """
    Get the stdout of a command as a list of split lines.

    Raise a BuildToolException if something went wrong

    """
    res = ""
    LOGGER.debug("calling: %s", " ".join(cmd))
    if DRYRUN:
        return [""]
    try:
        process = subprocess.Popen(cmd, cwd=cwd, env=env,
                                   stdout=subprocess.PIPE)
        res = process.communicate()[0].split("\n")
    except OSError as e:
        _raise_error(cmd, cwd, shell, e)
    except CalledProcessError as e:
        _raise_error(cmd, cwd, shell, e)
    return res


def _raise_error(cmd, cwd, shell, exception=None, retcode=None, output=None):
    """
    Raise a BuildToolException with a nice message

    """
    mess = "qitools.command failed\n"
    if exception:
        mess += "# error  : %s\n" % (exception)
    if retcode:
        mess += "# error  : retcode is %d\n" % (retcode)
    if cwd is not None:
        mess += "# workdir: %s\n" % (cwd)
    mess += "# run in shell: %s\n" % (shell)
    mess += "# command: %s\n" % " ".join(cmd)
    if output and len(output):
        mess += "# output: %s\n" % "\n".join(output)
    raise CommandFailedException(mess)

