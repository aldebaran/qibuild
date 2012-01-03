## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" This module contains a few functions for running CMake
and building projects.

"""

import os
import re
import logging

from . import toc
from . import parsers
from . import command
from . import configstore
from . import cmdparse
from . import ctest
from . import log
from . import worktree
from . import archive
from . import sh
from . import interact
from . import envsetter

from qibuild.toc        import toc_open
from qibuild.worktree import worktree_open
from qibuild.cmdparse   import run_action

__all__ = ( 'toc', 'parsers', 'command', 'configstore', 'cmdparse',
            'log', 'worktree', 'archive', 'sh', 'interact',
            'worktree_open', 'toc_open', 'run_action',
            'check_root_cmake_list', 'cmake', 'msbuild', 'make', 'nmake', 'get_cmake_qibuild_dir',
            'EnvSetter'
            )

LOGGER = logging.getLogger("qibuild")

QIBUILD_ROOT_DIR  = os.path.dirname(os.path.abspath(__file__))

# FIXME: filter this in using platform information ?
KNOWN_CMAKE_GENERATORS = [
        "Unix Makefiles",
        "Eclipse CDT4 - Unix Makefiles",
        "Visual Studio 9 2008",
        "Visual Studio 10",
        "Xcode",
        "NMake Makefiles",
]


def get_cmake_qibuild_dir():
    """Get the path to cmake modules.

    First, assume we are using qibuild from sources,
    then assume we are using an installed version of qibuild,

    Returns None if nothing was found
    """
    # First, assume this file is not installed,
    # so we have the python code in qibuild/python,
    # and the cmake code in qibuild/cmake
    # (using qibuild from sources)
    res = os.path.join(QIBUILD_ROOT_DIR, "..", "..", "cmake")
    res = sh.to_native_path(res)
    if os.path.isdir(res):
        return res

    # Then, assume we are in a toolchain or/in a SDK, with
    # the following layout sdk/share/cmake/qibuild, sdk/lib/python2.x/site-packages/qibuild
    sdk_dir = os.path.join(QIBUILD_ROOT_DIR, "..",  "..", "..", "..")
    sdk_dir = sh.to_native_path(sdk_dir)
    res = os.path.join(sdk_dir, "share", "cmake")
    if os.path.isdir(res):
        return res

    mess  = "Could not find qibuild cmake framework path\n"
    mess += "Please file a bug report with the details of your installation"
    raise Exception(mess)


def make(build_dir, num_jobs=None, target=None):
    """ Launch make from a build dir.
    Launch make -j <num_jobs> in num_jobs is not none

    """
    cmd = ["make"]
    if num_jobs is not None:
        cmd += ["-j%i" % num_jobs]
    if target:
        cmd.append(target)
    command.call(cmd, cwd=build_dir)


def nmake(build_dir, target=None):
    """ Launch nmake from a build dir.
    For this to work, you may need to be in a Visual
    Studio command prompt, or having run vcvarsall.bar
    """
    cmd = ["nmake"]
    if target:
        cmd.append(target)
    command.call(cmd, cwd=build_dir)



def msbuild(sln_file, build_type="Debug", target=None, num_jobs=None):
    """ Launch msbuild with correct configuration
    (debug or release), and with correct switch if num_jobs is not None
    """
    msbuild_conf = "/p:Configuration=%s" % build_type

    cmd = ["MSBuild.exe", msbuild_conf]
    cmd += ["/nologo"]
    if num_jobs != None:
        cmd.append("/m:%d" % int(num_jobs))

    if target is not None:
        cmd += ["/target:%s" % target]

    cmd += [sln_file]

    command.call(cmd)

def cmake(source_dir, build_dir, cmake_args, clean_first=True, env=None):
    """Call cmake with from a build dir for a source dir.
    cmake_args are added on the command line.

    If clean_first is True, we will remove cmake-generated files.
    Useful when dependencies have changed.

    """
    if not os.path.exists(source_dir):
        raise Exception("source dir: %s does not exist, aborting")

    # When calling qibuild configure, we know that the directory
    # exists, (for instance because we've just generated the dependencies.cmake file)
    # but when calling 'qibuild install', we call cmake to
    # set CMAKE_INSTALL_PREFIX of "/", but we do NOT know if the build
    # directory exists...
    if not os.path.exists(build_dir):
        mess  = "Could not find build directory: %s \n" % build_dir
        mess += "If you were trying to install the project, make sure "
        mess += "that you have configured and built it first"
        raise Exception(mess)

    # Always remove CMakeCache
    if clean_first:
        cache = os.path.join(build_dir, "CMakeCache.txt")
        sh.rm(cache)

    # Check that no one has made an in-source build
    in_source_cache = os.path.join(source_dir, "CMakeCache.txt")
    if os.path.exists(in_source_cache):
        # FIXME: better wording
        mess  = "You have run CMake from your sources\n"
        mess += "CMakeCache.txt found here: %s\n" % in_source_cache
        mess += "Please clean your sources and try again\n"
        raise Exception(mess)

    # Check that the root CMakeLists file is correct
    root_cmake = os.path.join(source_dir, "CMakeLists.txt")
    check_root_cmake_list(root_cmake, os.path.basename(source_dir))

    # Add path to source to the list of args, and set buildir for
    # the current working dir.
    cmake_args += [source_dir]
    command.call(["cmake"] + cmake_args, cwd=build_dir, env=env)



def read_cmake_cache(cache_path):
    """ Read a CMakeCache.txt file, returning a dict
    name -> value

    """
    with open(cache_path, "r") as fp:
        lines = fp.readlines()
    res = dict()
    for line in lines:
        if line.startswith("//"):
            continue
        if line.startswith("#"):
            continue
        if not line:
            continue
        match = re.match(r"([a-zA-Z-_]+):(\w+)=(.*)", line)
        if not match:
            continue
        else:
            (key, _type, value) = match.groups()
            res[key] = value
    return res


def check_root_cmake_list(cmake_list_file, project_name):
    """Check that the root CMakeLists.txt
    is correct.

    Those checks are necessary for cross-compilation to work well,
    among other things.
    """
    # Check that the root CMakeLists contains a project() call
    # The call to project() is necessary for cmake --build
    # to work when used with Visual Studio generator.
    lines = list()
    with open(cmake_list_file, "r") as fp:
        lines = fp.readlines()

    project_line_number = None
    include_line_number = None
    for (i, line) in enumerate(lines):
        if re.match(r'^\s*project\s*\(', line, re.IGNORECASE):
            project_line_number = i
        if re.match(r'^\s*include\s*\(.*qibuild\.cmake.*\)', line, re.IGNORECASE):
            include_line_number = i

    if project_line_number is None:
        mess  = """Incorrect CMakeLists file detected !

Missing call to project().
Please fix this by editing {cmake_list_file}
so that it looks like

cmake_minimum_required(VERSION 2.8)
project({project_name})
include(qibuild.cmake)

""".format(
        cmake_list_file=cmake_list_file,
        project_name=project_name)
        LOGGER.warning(mess)
        return

    if include_line_number is None:
        # Using qibuild command line, but not the qiBuild framework:
        # -> nothing to do ;)
        return

    if project_line_number > include_line_number:
        mess  = """Incorrect CMakeLists file detected !

The call to include(qibuild.cmake) should be AFTER the call to project()
Please exchange the following lines:

{cmake_list_file}:{include_line_number} {include_line}
{cmake_list_file}:{project_line_number} {project_line}

""".format(
            cmake_list_file=cmake_list_file,
            include_line_number=include_line_number,
            project_line_number=project_line_number,
            include_line=lines[include_line_number],
            project_line=lines[project_line_number])
        LOGGER.warning(mess)
