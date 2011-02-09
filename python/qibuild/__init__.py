## Copyright (C) 2011 Aldebaran Robotics

"""
This module contains build function for
unix-like systems or Visual Studio

Gotcha:
=======
Calling cmake -DCMAKE_BUILD_TYPE=debug and
msbuild foo.sln causes foo to be build in release.
(it's a CMake / visual studio "feature")

This is why we should keep the same build dir on windows
"""

import os
import logging
import qitools.sh
import qitools.command

import parsers
import toc
from toc import toc_open

LOGGER = logging.getLogger("qibuild")

def make(build_dir, num_jobs=None, target=None):
    """
    Just launch make from a build dir.
    Lanch make -j <num_jobs> in num_jobs is not none

    """
    cmd = ["make"]
    if num_jobs is not None:
        cmd += ["-j%i" % num_jobs]
    if target:
        cmd.append(target)
    qitools.command.check_call(cmd, cwd=build_dir)


def nmake(build_dir, target=None):
    """Just launch nmake from a build dir.
    For this to work, you'd better be in a Visual
    Studio command prompt
    """
    cmd = ["nmake"]
    if target:
        cmd.append(target)
    qitools.command.check_call(cmd, cwd=build_dir)


def msbuild(sln_file, build_type="Debug", be_verbose=False, target="ALL_BUILD"):
    """
    Launch msbuild with correct configuratrion
    (debug or release),
    and with correct switch if num_jobs is not None
    """
    msbuild_conf = "/p:Configuration=%s" % build_type

    cmd = ["MSBuild.exe", msbuild_conf]
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

    qitools.command.check_call(cmd)

def cmake(source_dir, build_dir, cmake_args):
    """
    Call cmake with from a build dir for a source dir.
    cmake_args are directly added on the command line

    The cache is always cleaned
    """
    if not os.path.exists(source_dir):
        raise Exception("source dir: %s does not exist, aborting")

    # Always remove CMakeCache and build/sdk/lib/cmake:
    cache = os.path.join(build_dir, "CMakeCache.txt")
    if os.path.exists(cache):
        os.remove(cache)
        LOGGER.debug("done cleaning cache")

    qitools.sh.rm(os.path.join(build_dir, "sdk", "lib", "cmake"))

    # Add path to source
    cmake_args += [source_dir]
    qitools.command.check_call(["cmake"] + cmake_args, cwd=build_dir)

def ctest(source_dir, build_dir):
    """
    Just run test using ctest.
    source_dir should contain CMakeLists.txt
    build_dir must have been configured (cmake) and built.

    """
    cmd = ["ctest", "-VV", "-DExperimental", source_dir ]
    # Check whether source_dir and build_dir look valid.
    # TODO: Move these checks in a common place?
    if not os.path.exists(source_dir):
        raise Exception("source dir: %s does not exist, aborting" % \
                             source_dir)
    if not os.path.exists(os.path.join(source_dir, "CMakeLists.txt")):
        raise Exception("source dir: %s does not contain CMakeLists,"\
                             " aborting" % source_dir)
    if not os.path.exists(build_dir):
        raise Exception("build dir: %s does not exist, aborting" % \
                             build_dir)
    if not os.path.exists(os.path.join(build_dir, "CMakeCache.txt")):
        raise Exception("build dir: %s does not contain "\
                             "CMakeCache.txt, aborting" % build_dir)

