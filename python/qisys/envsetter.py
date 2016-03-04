## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

r""" This module contains the :py:class:`EnvSetter` class,
designed to take care of environment variables.


"""
import os
import sys
import subprocess

import qisys.error
import qisys.sh

class EnvSetter(object):
    r""" A class to manage environment variables

    Typical usage::

        envsetter = EnvSetter()
        envsetter.prepend_to_path(r"c:\path\to\cmake")
        envsetter.set_env_var("WITH_SPAM", "ON")
        envsetter.source_bat(r"C:\path\to\vcvars.bat")
        build_env = envsetter.get_build_env()
        # build_env is now a *copy* of os.environ, os.environ does
        # NOT change
        qisys.command.call("cmake", env=build_env)

    Notes:

    * this will work even if ``cmake`` was not in ``%PATH%`` before,
      because we will use ``build_env`` when searching for ``cmake``.
      (see :py:func:`qisys.command.call` documentation)

    * the :py:meth:`source_bat` function is useful to use ``cl.exe`` and
      ``NMake Makefiles``. In this case, you have to source ``vsvarsall.bat``.

    """
    # Note: always use .copy() when working with dict, else you end up
    # returning a *reference* to the directory ...
    def __init__(self, build_env=None):
        if not build_env:
            build_env = os.environ.copy()
        self._build_env = build_env

    def get_build_env(self):
        """ Returns a dictionary containing the new environment
        (note that ``os.environ`` is preserved)
        """
        return self._build_env.copy()

    def set_env_var(self, variable, value):
        """ Set a new variable

        """
        self._build_env[variable] = value

    def prepend_directory_to_variable(self, directory, variable):
        """ Append a new directory to an environment variable
        containing a list of paths (most of the time PATH, but
        can be LIBDIR, for instance when using cl.exe)

        * The path will always be sanitize first
            (absolute, native path)

        * No directory will be added twice

        * The variable will be put in upper case on the dictionary
          on windows.

        """
        # ":" on unix, ";" on windows
        pathsep = os.path.pathsep

        # always sanitize inputs:
        # on windows, upper-case the env var (just in case)
        if sys.platform.startswith("win"):
            variable = variable.upper()
        directory = qisys.sh.to_native_path(directory)

        old_value = self._build_env.get(variable, "")
        # avoid having empty paths:
        if old_value.endswith(pathsep):
            old_value = old_value[:-1]
        splitted_paths = old_value.split(pathsep)
        if directory in splitted_paths:
            splitted_paths.remove(directory)

        splitted_paths.insert(0, directory)

        self._build_env[variable] = pathsep.join(splitted_paths)

    def prepend_to_path(self, directory):
        """ Append a directory to PATH environment variable

        """
        self.prepend_directory_to_variable(directory, "PATH")


    def source_bat(self, bat_file):
        """Set environment variables using a .bat script

        Note: right now, this only works well with vcvarsall.bat scripts.

        """
        # Quick hack to get env vars from a .bat script
        # (stolen idea from distutils/msvccompiler)
        # TODO: handle non asccii chars?
        # Hint: decode("mcbs") ...
        if not os.path.exists(bat_file):
            raise qisys.error.Error(
                    "bat file (%s) does not exist" % bat_file)

        # set of environment variables that are in fact list of paths
        # FIXME: what should we do with other env?
        # FIXME: how can we avoid to hardcode this?
        interesting = set(("INCLUDE", "LIB", "LIBPATH", "PATH"))
        result = {}

        process = subprocess.Popen('"%s"& set' % (bat_file),
                             stdout=subprocess.PIPE,
                             shell=True)
        (out, err) = process.communicate()
        if process.returncode != 0:
            mess  = "Calling %s failed\n" % bat_file
            mess += "Error was: %s" % err
            raise qisys.error.Error(mess)

        #pylint: disable-msg=E1103
        for line in out.split("\n"):
            if '=' not in line:
                continue
            line = line.strip()
            key, value = line.split('=', 1)
            key = key.upper()
            if key in interesting:
                if value.endswith(os.pathsep):
                    value = value[:-1]
                result[key] = value

        for (variable, directories_list) in result.iteritems():
            directories = directories_list.split(os.path.pathsep)
            for directory in directories:
                self.prepend_directory_to_variable(directory, variable)


    def read_config(self, qibuild_cfg):
        """ Read a :py:class:`qibuild.config.QiBuildConfig` instance

        """
        bat_file = qibuild_cfg.env.bat_file
        if bat_file:
            self.source_bat(bat_file)
        path_env = qibuild_cfg.env.path
        if path_env:
            self.prepend_to_path(path_env)
        env_vars = qibuild_cfg.env.vars
        self._build_env.update(env_vars)
