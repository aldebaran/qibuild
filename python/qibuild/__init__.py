## Copyright (C) 2011 Aldebaran Robotics

""" This module contains a few functions for running CMake
and building projects.

"""

import os
import logging
import qitools.sh
import qitools.command

import parsers
import toc
from toc import toc_open

LOGGER = logging.getLogger("qibuild")

QIBUILD_ROOT_DIR  = os.path.dirname(os.path.abspath(__file__))

def get_cmake_qibuild_dir():
    """Get the path to cmake modules.

    Useful to copy qibuild.cmake template in
    qibuild create, among other things.

    """
    # First, assume this file is not installed,
    # so we have the python code in qibuild/python,
    # and the cmake code in qibuild/cmake:
    res = os.path.join(QIBUILD_ROOT_DIR, "..", "..", "cmake", "qibuild")
    if os.path.isdir(res):
        return qitools.sh.to_native_path(res)

    # Else, try to import qibuild.config, a
    # python module configured by cmake during installation,
    # containing CMAKE_ROOT
    from qibuild.config import CMAKE_ROOT
    res = os.path.join(CMAKE_ROOT, "Modules", "qibuild")
    if os.path.isdir(res):
        return qitools.sh.to_native_path(res)

    raise Exception("Could not find qibuild cmake root dir!")

CMAKE_QIBUILD_DIR = get_cmake_qibuild_dir()


def make(build_dir, num_jobs=None, target=None):
    """ Launch make from a build dir.
    Launch make -j <num_jobs> in num_jobs is not none

    """
    cmd = ["make"]
    if num_jobs is not None:
        cmd += ["-j%i" % num_jobs]
    if target:
        cmd.append(target)
    qitools.command.check_call(cmd, cwd=build_dir)


def nmake(build_dir, target=None):
    """ Launch nmake from a build dir.
    For this to work, you may need to be in a Visual
    Studio command prompt, or having run vcvarsall.bar
    """
    cmd = ["nmake"]
    if target:
        cmd.append(target)
    qitools.command.check_call(cmd, cwd=build_dir)


def msbuild(sln_file, build_type="Debug", be_verbose=False, target="ALL_BUILD"):
    """ Launch msbuild with correct configuration
    (debug or release), and with correct switch if num_jobs is not None
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

def cmake(source_dir, build_dir, cmake_args, clean_first=True):
    """Call cmake with from a build dir for a source dir.
    cmake_args are added on the command line.

    If clean_first is True, we will remove cmake-generated files.
    Useful when dependencies have changed.

    """
    if not os.path.exists(source_dir):
        raise Exception("source dir: %s does not exist, aborting")

    # Always remove CMakeCache and sdk/lib/cmake
    # (CMake does not always do the right thing when .cmake
    # files change)
    if clean_first:
        cache = os.path.join(build_dir, "CMakeCache.txt")
        qitools.sh.rm(cache)
        qitools.sh.rm(os.path.join(build_dir, "sdk", "lib", "cmake"))

    # Check that no one has made an in-source build
    in_source_cache = os.path.join(source_dir, "CMakeCache.txt")
    if os.path.exists(in_source_cache):
        # FIXME: better wording
        mess  = "You have run CMake from your sources\n"
        mess += "CMakeCache.txt found here: %s\n" % in_source_cache
        mess += "Please clean your sources and try again\n"
        raise Exception(mess)

    # Add path to source to the list of args, and set buildir for
    # the current working dir.
    cmake_args += [source_dir]
    qitools.command.check_call(["cmake"] + cmake_args, cwd=build_dir)


