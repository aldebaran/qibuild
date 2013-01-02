## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module contains function to handle CMake managed project.

"""

import os
import re
import subprocess
import qisys.log

from qisys import ui
import qisys.command
import qisys.sh
import qibuild.cmake.profiling

def get_known_cmake_generators():
    """ Get the list of known cmake generators.
    Assume cmake is in PATH, or path to cmake is correctly
    configured in ~/.config/qi/qibuild.xml

    """
    build_env = qibuild.config.get_build_env()
    cmake_    = qisys.command.find_program("cmake", env=build_env)
    if not cmake_:
        message = """\
Could not find cmake executable
Please install it if necessary and re-run `qibuild config --wizard`\
"""
        raise Exception(message)
    process = subprocess.Popen([cmake_, "--help"], stdout=subprocess.PIPE)
    (out, _err) = process.communicate()
    intersting  = False
    intersting_lines = list()
    magic_line = "The following generators are available on this platform:"
    # pylint: disable-msg=E1103
    for line in out.splitlines():
        # handle lines like that:
        # Generator = "blalblalba"
        #       files.
        if len(line) >= 3:
            if line[2] == ' ' and not "=" in line:
                continue
        if line == magic_line:
            intersting = True
            continue
        if intersting:
            intersting_lines.append(line)
    to_parse = ""
    for line in intersting_lines:
        to_parse += line.strip()
        # handle lines like that:
        #   Generator
        #           = "blabla"
        if "=" in line:
            to_parse += "\n"
    res = list()
    for line in to_parse.splitlines():
        generator = line.split("=")[0]
        res.append(generator.strip())
    return res


def get_cached_var(build_dir, var, default=None):
    """Get a variable from cmake cache

    :param build_dir: CMakeCache.txt file directory
    :param var:       Requested variable
    :param default:   Default value if not found (default: None)

    :return: the variable value

    """
    cmakecache = os.path.join(build_dir, "CMakeCache.txt")
    if not os.path.exists(cmakecache):
        mess  = "Could not find CMakeCache.txt in %s" % build_dir
        raise Exception(mess)
    res = read_cmake_cache(cmakecache)
    return res.get(var, default)


def cmake(source_dir, build_dir, cmake_args, env=None,
          clean_first=True, profiling=False):
    """Call cmake with from a build dir for a source dir.
    cmake_args are added on the command line.

    If clean_first is True, we will remove cmake-generated files.
    Useful when dependencies have changed.

    """
    if not os.path.exists(source_dir):
        raise Exception("source dir: %s does not exist, aborting")

    if not os.path.exists(build_dir):
        mess  = "Could not find build directory: %s \n" % build_dir
        raise Exception(mess)

    # Always remove CMakeCache
    if clean_first:
        cache = os.path.join(build_dir, "CMakeCache.txt")
        qisys.sh.rm(cache)

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
    if not profiling:
        qisys.command.call(["cmake"] + cmake_args, cwd=build_dir, env=env)
        return
    # importing here in order to not create circular dependencies:
    cmake_log = os.path.join(build_dir, "cmake.log")
    fp = open(cmake_log, "w")
    ui.info(ui.green, "Running cmake for profiling ...")
    subprocess.call(["cmake"] + cmake_args, cwd=build_dir, env=env,
                   stdout=fp, stderr=fp)
    fp.close()
    qibuild_dir = get_cmake_qibuild_dir()
    ui.info(ui.green, "Analyzing cmake logs ...")
    profiling_res = qibuild.cmake.profiling.parse_cmake_log(cmake_log, qibuild_dir)
    outdir = os.path.join(build_dir, "profile")
    qibuild.cmake.profiling.gen_annotations(profiling_res, outdir, qibuild_dir)
    ui.info(ui.green, "Annotations generated in", outdir)


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
        match = re.match(r"([a-zA-Z0-9-_]+):(\w+)=(.*)", line)
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
        if re.match(r'^\s*include\s*\(.*qibuild\.cmake.*\)', line,
                    re.IGNORECASE):
            include_line_number = i

    if project_line_number is None:
        mess  = """Incorrect CMakeLists file detected !

Missing call to project().
Please fix this by editing {cmake_list_file}
so that it looks like

cmake_minimum_required(VERSION 2.8)
project({project_name})
find_package(qibuild)

""".format(
            cmake_list_file=cmake_list_file,
            project_name=project_name)
        ui.warning(mess)
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
        ui.warning(mess)


def get_cmake_qibuild_dir():
    """Get the path to cmake modules.

    First, assume we are using qibuild from sources,
    then assume we are using an installed version of qibuild.
    """
    # First, assume this file is not installed,
    # so we have the python code in qibuild/python,
    # and the cmake code in qibuild/cmake
    # (using qibuild from sources)
    res = os.path.join(qibuild.QIBUILD_ROOT_DIR, "..", "..", "cmake")
    res = qisys.sh.to_native_path(res)
    if os.path.isdir(res):
        return res

    # Then, assume we are in a toolchain or/in a SDK, with
    # the following layout sdk/share/cmake/qibuild,
    # sdk/lib/python2.x/site-packages/qibuild
    sdk_dir = os.path.join(qibuild.QIBUILD_ROOT_DIR, "..", "..", "..", "..")
    sdk_dir = qisys.sh.to_native_path(sdk_dir)
    res = os.path.join(sdk_dir, "share", "cmake")
    if os.path.isdir(res):
        return res

    mess  = "Could not find qibuild cmake framework path\n"
    mess += "Please file a bug report with the details of your installation"
    raise Exception(mess)


def get_binutil(name, cmake_var=None, build_dir=None, build_env=None):
    """ Get a tool from the binutils package.
    First, look for it in the CMake cache, else look for it in the
    system.

    Note that after a call to CMAKE_FORCE_C_COMPILER() in a CMake
    toolchain file, CMAKE_AR, CMAKE_OBJDUMP et al. should be correctly
    set in cache.

    """
    res = None
    if not cmake_var:
        cmake_var = "CMAKE_" + name.upper()
    if build_dir:
        res =  get_cached_var(build_dir, cmake_var)
    if res:
        return res
    return qisys.command.find_program(name, env=build_env)
