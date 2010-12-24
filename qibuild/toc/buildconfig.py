##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

"""This module contains:

The BuildConfig class, which stores a build configuration,
and the BuildConfigManager class, which makes the glue
betwenn the Project and its BuildConfig


Gotcha 1:
=========

Assuming a config file looks like:

[project foo]
cmake.flags = "-DFOO=BAR"

What to do when user calls toc cmake -DSPAM=EGGS ?

# Option 1: we ignore flags from configuration, so we call
cmake -DSPAM=EGGS

# Option 2: we append the new flags to the configuration, so we call:
cmake -DFOO=BAR -DSPAM=EGGS


BUT :

option 1 has a nasty consequence: since flags are stored in CMakeCache
(and since toc always deletes the cache)
calling :

toc cmake -DSPAM=EGGS foo

will cause SPAM=EGGS to be in the cache, but not FOO=BAR
(which may be weird for the end user)


Right now, we are sticking to option 2, so that it does not matter
whereas you've cleaned your cache or not.

If you really do not want to no have the option FOO=BAR, you have to erase
the cmake.flags setting in your personal config file (~/.toc/base.cfg)


Gotcha 2:
========

Calling cmake -DCMAKE_BUILD_TYPE=debug and
msbuild foo.sln causes foo to be build in release.
(it's a CMake / visual studio "feature")

This is why we keep the same build dir on windows
"""

import os
import shlex

class BuildConfig:
    """A build configuration has:
      * a set of CMake flags
      * a toolchain_name

      There's  a bunch of update_* method that
      any class can call
    """
    def __init__(self):
        self.cmake_flags     = list()
        self.build_directory = None

    def update(self, tob, project, build_directory_name):
        """ Update cmake_flags
           - add flags from the build_config
           - add flags from the project config
           - add flags from the command line
        """
        if tob.build_config:
            build_config_flags = tob.configstore.get("build", tob.build_config, "cmake", "flags", default=None)
            if build_config_flags:
                self.cmake_flags.extend(shlex.split(build_config_flags))

        project_flags = tob.configstore.get(project.name, "build", "cmake", "flags", default=None)
        if project_flags:
            self.cmake_flags.extend(shlex.split(project_flags))

        if tob.build_type:
            self.flags.append("CMAKE_BUILD_TYPE=%s" % (tob.build_type.toupper()))

        if tob.toolchain_name:
            self.flags.append("QI_TOOLCHAIN_NAME=%s" % (tob.toolchain_name))

        if tob.cmake_flags:
            # See big __doc__ for why we use append here
            self.cmake_flags.extend(tob.cmake_flags)
        self.build_directory = os.path.join(project.directory, build_directory_name)
        #create the build_directory if it does not exists
        if not os.path.exists(self.build_directory):
            os.makedirs(self.build_directory)



    def __str__(self):
        res = ""
        res += "  cmake_flags     = %s\n"     % self.cmake_flags
        res += "  build_directory = %s\n" % self.build_directory
        return res
