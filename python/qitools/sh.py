##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

""" sh like functions """

import sys
import os
import shutil
import logging
import subprocess

LOGGER = logging.getLogger("buildtool.sh")

def mkdir(dest_dir, recursive=False):
    """ recursive mkdir (do not fail if file exists) """
    try:
        if recursive:
            os.makedirs(dest_dir)
        else:
            os.mkdir(dest_dir)
    except OSError, e:
        if e.errno == 17:
            pass
        else:
            raise

#pylint: disable-msg=C0103
def ln(src, dst, symlink=True):
    """ ln (do not fail if file exists) """
    try:
        if symlink:
            os.symlink(src, dst)
        else:
            raise NotImplementedError
    except OSError, e:
        if e.errno == 17:
            pass
        else:
            raise


def rm(name):
    """This one can take a file or a directory.
    Contrary to shutil.remove or os.remove, it:

    * won't fail if the directory does not exists
    * won't fail if the directory contains read-only files
    * won't fail if the file does not exists

    Please avoid using shutil.rmtree ...
    """
    if not os.path.exists(name):
        return
    def _rmtree_handler(func, path, _execinfo):
        """Call by rmtree when there was an error.

        if this is called because we could not remove a file, then see if
        it is readonly, change it back to nornal and try again

        """
        import stat
        if (func == os.remove) and not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWRITE)
            os.remove(path)
        else:
            # Something else must be wrong...
            raise

    if os.path.isdir(name):
        LOGGER.debug("Removing directory: %s", name)
        shutil.rmtree(name, False, _rmtree_handler)
    else:
        LOGGER.debug("Removing %s", name)
        os.remove(name)


def ls_r(directory):
    """Returns a sorted list of all the files present in a diretory,
    relative to this directory.

    For instance, with:

    foo
    |-- eggs
    |   |-- c
    |   |-- d
    |-- empty
    |-- spam
    |   |-- a
    |   |-- b

    ls_r(foo) returns:
    ["eggs/c", "eggs/d", "empty/", "spam/a", "spam/b"]

    """
    res = list()
    for root, dirs, files in os.walk(directory):
        new_root = os.path.relpath(root, directory)
        if new_root == "." and not files:
            continue
        if new_root == "." and files:
            res.extend(files)
            continue
        if not files and not dirs:
            res.append(new_root + os.path.sep)
            continue
        for f in files:
            res.append(os.path.join(new_root, f))
    res.sort()
    return res

def which(program):
    """
    find program in the environment PATH
    @return path to program if found, None otherwise
    """
    for path in os.getenv('PATH').split(':'):
        if os.path.exists(path) and program in os.listdir(path):
            return os.path.join(path, program)
    return None


def run(program, args):
    """ exec a process.
        linux: this will call exec and replace the current process
        win  : this will call spawn and wait till the end
        ex:
        run("python.exe", "toto.py")
    """
    real_args = [ program ]
    real_args.extend(args)

    if sys.platform.startswith("win32"):
        retcode = 0
        try:
            retcode = subprocess.call(real_args)
        except subprocess.CalledProcessError:
            print "problem when calling", program
            retcode = 2
        sys.exit(retcode)
        return

    os.execvp(program, real_args)

def to_posix_path(path):
    """
    Returns a POSIX path from a DOS path

    Useful because cmake *needs* POSIX paths.

    Guidelines:
        * always use os.path insternally
        * convert to POXIS path at the very last moment

    """
    res = os.path.expanduser(path)
    res = os.path.abspath(res)
    res = path.replace("\\", "/")
    return res

def to_dos_path(path):
    """Return a DOS path from a "windows with /" path.
    Useful because people sometimes use forward slash in
    env var
    """
    res = path.replace("/", "\\")
    return res
