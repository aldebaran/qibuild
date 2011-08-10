## Copyright (C) 2011 Aldebaran Robotics

r""" This module contains the EnvSetter class,
designed to take care of environnement variables.


"""
import os
import sys

import qibuild

class EnvSetter():
    r""" A class to manager environnement variables

    Typical usage::

        envsetter = EnvSetter()
        envsetter.append_directory_to_path(r"c:\path\to\cmake", "PATH")
        envsetter.source_bat(r"C:\path\to\vcvars.bat")
        build_env = envsetter.get_build_env()
        # build_env is now a *copy* of os.environ, os.environ does
        # NOT change
        qibuild.command.call("cmake", env=build_env)

    Note1: this will work even in cmake was not in %PATH% before,
    because we will use build_env when searching for 'cmake'.
    see qibuild.command.call documentation

    Note2: this is a nice way to set cmake (or git) in a config file
    withouth to mess up with %PATH% on windows

    Note3: the source_bat() function is mandatory to use cl.exe and
    NMake Makefiles. (you usually have to source vsvarsall.bat)


    """
    # Note: always use .copy() when working with dict, else you end up
    # returning a *reference* to the directory ...
    def __init__(self):
        self._build_env = os.environ.copy()

    def get_build_env(self):
        return self._build_env.copy()

    def append_directory_to_variable(self, directory, variable):
        """ Append a new directory to an environnement variable
        containing a list of paths (most of the time PATH, but
        can be LIBDIR, for instance when using cl.exe)

        * The path will always be sanitize first
            (absolute, native path)

        * No directory will be added twice

        * The variable will be put in upper case on the dictionnary
          on windows.

        """
        # ":" on unix, ";" on windows
        pathsep = os.path.pathsep

        # always sanitize inputs:
        # on windows, upper-case the env var (just in case)
        if sys.platform.startswith("win"):
            variable = variable.upper()
        directory = qibuild.sh.to_native_path(directory)

        old_value = self._build_env[variable]
        # avoid having empty paths:
        if old_value.endswith(pathsep):
            old_value = old_value[:-1]
        splitted_paths = old_value.split(pathsep)
        if directory not in splitted_paths:
            splitted_paths.append(directory)

        self._build_env[variable] = pathsep.join(splitted_paths)

    def append_to_path(self, directory):
        """ Just a shorthand """
        self.append_directory_to_variable(directory, "PATH")


    def source_bat(self, bat_file):
        pass

