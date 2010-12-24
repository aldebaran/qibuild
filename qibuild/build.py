##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""
This module contains build function for
unix-like systems or Visual Studio

"""

import os
import sys
import glob
import logging
import qibuild.sh
import qibuild.command


LOGGER = logging.getLogger("qibuild.build")

CMAKE        = "cmake"
MAKE         = "make"
MSBUILD      = None
INCREDIBUILD = None
NMAKE        = None

if sys.platform.startswith("win32"):
    CMAKE = "cmake.exe"

class MakeException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

class ConfigureException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)


def build_unix(build_dir, num_jobs=None, target=None):
    """
    Just launch make from a build dir.
    Lanch make -j <num_jobs> in num_jobs is not none

    """
    cmd = [MAKE]
    if num_jobs is not None:
        cmd += ["-j%i" % num_jobs]
    if target:
        cmd.append(target)
    qibuild.command.check_call(cmd, cwd=build_dir)


def build_nmake(build_dir, target=None):
    """Just launch nmake from a build dir.
    For this to work, you'd better be in a Visual
    Studio command prompt
    """
    if NMAKE is None:
        raise MakeException("Could not find nmake")
    cmd = [NMAKE]
    if target:
        cmd.append(target)
    qibuild.command.check_call(cmd, cwd=build_dir)


def build_vc(sln_file, release=False, be_verbose=True, target=None):
    """
    Launch msbuild with correct configuratrion
    (debug or release),
    and with correct switch if num_jobs is not None
    """

    if MSBUILD is None:
        raise MakeException("Could not find msbuild.exe")
    if not target:
        target="ALL_BUILD"
    # Use incredibuild if available
    if INCREDIBUILD is not None:
        build_incredibuild(sln_file, release, be_verbose, target)
        return

    if release:
        msbuild_conf = "/p:Configuration=Release"
    else:
        msbuild_conf = "/p:Configuration=Debug"

    LOGGER.debug("building " + sln_file)

    cmd = [MSBUILD, msbuild_conf]
    cmd += ["/nologo"]

    if be_verbose:
        # PerformanceSummary:
        # Displays the time spent in tasks, targets, and projects.
        # NoItemAndPropertyList:

        # Hides the list of items and properties displayed at the
        # start of each project build in diagnostic verbosity

        # Verbosity:
        # The available verbosity levels are q[uiet], m[inimal],
        # n[ormal], d[etailed], and diag[nostic].

        cmd += ["/clp:PerformanceSummary;NoItemAndPropertyList;Summary;Verbosity=normal"]


    if target is not None:
        cmd += ["/target:%s" % target]

    cmd += [sln_file]

    qibuild.command.check_call(cmd)

def build_incredibuild(sln_file, release=False, be_verbose=True, target="ALL_BUILD"):
    """
    Incredibuild build
    """
    cmd = [INCREDIBUILD, sln_file]

    if release:
        cmd += ["/cfg=Release|Win32"]
    else:
        cmd += ["/cfg=Debug|Win32"]

    # rather too much information, especially showcmd, but it shows how
    # poor our include structure is.
    #if be_verbose:
    #    cmd += ["/SHOWAGENT", "/SHOWTIME", "/SHOWCMD"]

    if target is not None:
        cmd += ["/PRJ=" + target]

    cmd += ["/nologo"]

    qibuild.command.check_call(cmd)

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

