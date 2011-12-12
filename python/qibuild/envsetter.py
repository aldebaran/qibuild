## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

r""" This module contains the EnvSetter class,
designed to take care of environment variables.


"""
import os
import sys
import subprocess

import qibuild

class EnvSetter():
    r""" A class to manager environment variables

    Typical usage::

        envsetter = EnvSetter()
        envsetter.append_to_path(r"c:\path\to\cmake")
        envsetter.set_env_var("WITH_SPAM", "ON")
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

    def set_env_var(self, variable, value):
        """ Set a new variable

        """
        self._build_env[variable] = value

    def append_directory_to_variable(self, directory, variable):
        """ Append a new directory to an environment variable
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

        old_value = self._build_env.get(variable, "")
        # avoid having empty paths:
        if old_value.endswith(pathsep):
            old_value = old_value[:-1]
        splitted_paths = old_value.split(pathsep)
        if directory not in splitted_paths:
            splitted_paths.append(directory)

        self._build_env[variable] = pathsep.join(splitted_paths)

    def append_to_path(self, directory):
        """ Append a directory to PATH environment variable

        """
        self.append_directory_to_variable(directory, "PATH")


    def source_bat(self, bat_file):
        """Set environment variables using a .bat script

        Note: right now, this only works well with vcvarsall.bat scripts in
        fact,

        """
        # Quick hack to get env vars from a .bat script
        # (stolen idea from distutils/msvccompiler)
        # TODO: handle non asccii chars?
        # Hint: decode("mcbs") ...
        if not os.path.exists(bat_file):
            raise Exception("general.env.bat_file (%s) does not exists" % bat_file)

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
            mess  = "Calling %s failed\n", bat_file
            mess += "Error was: %s" % err
            raise Exception(mess)

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
                self.append_directory_to_variable(directory, variable)
