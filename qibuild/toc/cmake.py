##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

import os
import sys
import logging
import qibuild.sh
import qibuild.command


class ConfigureException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

CMAKE = "cmake"
if sys.platform.startswith("win32"):
    CMAKE = "cmake.exe"

LOGGER = logging.getLogger("qibuild.toc.cmake")

def cmake(source_dir, build_dir, cmake_args):
    """
    Call cmake with from a build dir for a source dir.
    cmake_args are directly added on the command line

    The cache is always cleaned
    """
    if not os.path.exists(source_dir):
        raise ConfigureException("source dir: %s does not exist, aborting")

    # Always remove CMakeCache and build/sdk/lib/cmake:
    cache = os.path.join(build_dir, "CMakeCache.txt")
    if os.path.exists(cache):
        os.remove(cache)
        LOGGER.debug("done cleaning cache")

    qibuild.sh.rm(os.path.join(build_dir, "sdk", "lib", "cmake"))

    # Add path to source
    cmake_args += [source_dir]
    qibuild.command.check_call([CMAKE] + cmake_args, cwd=build_dir)


def configure_project(project, flags=None, toolchain_file=None, generator=None):
    """ Call cmake with correct options
    if toolchain_file is None a t001chain file is generated in the cmake binary directory.
    if toolchain_file is "", then CMAKE_TOOLCHAIN_FILE is not specified.
    """

    #TODO: guess generator

    if not os.path.exists(project.directory):
        raise ConfigureException("source dir: %s does not exist, aborting" % project.directory)

    if not os.path.exists(os.path.join(project.directory, "CMakeLists.txt")):
        LOGGER.info("Not calling cmake for %s", os.path.basename(project.directory))
        return

    # Set generator (mandatory on windows, because cmake does not
    # autodetect visual studio compilers very well)
    cmake_args = []
    if generator:
        cmake_args.extend(["-G", generator])

    # Make a copy so that we do not modify
    # the list used by the called
    if flags:
        cmake_flags = flags[:]
    else:
        cmake_flags = list()
    cmake_flags.extend(project.build_config.cmake_flags)

    if toolchain_file:
        cmake_flags.append("CMAKE_TOOLCHAIN_FILE=" + toolchain_file)

    cmake_args.extend(["-D" + x for x in cmake_flags])

    cmake(project.directory, project.build_config.build_directory, cmake_args)


