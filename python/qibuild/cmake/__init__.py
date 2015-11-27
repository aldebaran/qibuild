## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module contains function to handle CMake managed project.

"""

import sys
import os
import re
import subprocess

from qisys import ui
import qisys.error
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
        raise qisys.error.Error(message)
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
    # Fix Visual Studio generators:
    fixed_list = list()
    for generator in res:
        if "Visual Studio" in generator and "[arch]" in generator:
            fixed_list.append(generator.replace(" [arch]", ""))
            fixed_list.append(generator.replace("[arch]", "Win64"))
            fixed_list.append(generator.replace("[arch]", "ARM"))
        else:
            fixed_list.append(generator)
    return fixed_list

def get_cmake_version(cmake_binary):
    """ Get CMake version number """
    output = subprocess.check_output([cmake_binary, "--version"])
    # output looks like:
    #   cmake version 3.4.20151013-g3d9cf
    #
    #   CMake suite maintained and supported by Kitware (kitware.com/cmake).
    # So take the last word of the first line
    first_line = output.splitlines()[0]
    words = first_line.split()
    return words[-1]

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
        raise qisys.error.Error(mess)
    res = read_cmake_cache(cmakecache)
    return res.get(var, default)

def cmake(source_dir, build_dir, cmake_args, env=None,
          clean_first=True, profiling=False, debug_trycompile=False,
          trace_cmake=False, summarize_options=False):
    """Call cmake with from a build dir for a source dir.
    cmake_args are added on the command line.

    :param env: defines the environment used when calling ``cmake``
                ``os.environ`` will remain unchanged
    :param clean_first: Clean the cmake cache
    :param summarize_options: Whether to call :py:func:`display_options` at the end

    For qibuild/CMake hackers:

    :param profiling: Profile CMake executions
    :param debug_trycompile: Call ``cmake`` with ``--debug-trycompile``
    :param trace_cmake: Call ``cmake`` with ``--trace`` The results
                        will be written in <build>/cmake.log

    """
    cmake_binary = qisys.command.find_program("cmake", env=env, raises=True)
    if not os.path.exists(source_dir):
        qisys.error.Error("source dir: %s does not exist, aborting")

    if not os.path.exists(build_dir):
        mess  = "Could not find build directory: %s \n" % build_dir
        qisys.error.Error(mess)

    # Always remove CMakeCache
    if clean_first:
        cache = os.path.join(build_dir, "CMakeCache.txt")
        qisys.sh.rm(cache)

    if debug_trycompile:
        cmake_args.append("--debug-trycompile")
    if profiling or trace_cmake:
        cmake_version = get_cmake_version(cmake_binary)
        if qisys.version.compare(cmake_version, "3.4") >= 0:
            cmake_args.append("--trace-expand")
        else:
            cmake_args.append("--trace")

    # Check that no one has made an in-source build
    in_source_cache = os.path.join(source_dir, "CMakeCache.txt")
    if os.path.exists(in_source_cache):
        # FIXME: better wording
        mess  = "You have run CMake from your sources\n"
        mess += "CMakeCache.txt found here: %s\n" % in_source_cache
        mess += "Please clean your sources and try again\n"
        qisys.error.Error(mess)

    # Check that the root CMakeLists file is correct
    root_cmake = os.path.join(source_dir, "CMakeLists.txt")
    check_root_cmake_list(root_cmake)

    # Add path to source to the list of args, and set buildir for
    # the current working dir.
    cmake_args += [source_dir]
    if not profiling and not trace_cmake:
        qisys.command.call([cmake_binary] + cmake_args, cwd=build_dir, env=env)
        if summarize_options:
            display_options(build_dir)
        return
    cmake_log = os.path.join(build_dir, "cmake.log")
    fp = open(cmake_log, "w")
    if profiling:
        ui.info(ui.green, "Running cmake for profiling ...")
    if trace_cmake:
        ui.info(ui.green, "Running cmake with --trace ...")
    ui.debug("Running cmake " + " ".join(cmake_args))
    retcode = subprocess.call([cmake_binary] + cmake_args, cwd=build_dir, env=env,
                   stdout=fp, stderr=fp)
    fp.close()
    if retcode != 0:
        mess = "CMake failed"
        if retcode < 0:
            mess += " (%s)" % qisys.command.str_from_signal(-retcode)
        ui.error(mess)
    ui.info(ui.green, "CMake trace saved in", ui.reset, ui.bold, cmake_log)
    if not profiling:
        return
    qibuild_dir = get_cmake_qibuild_dir()
    ui.info(ui.green, "Analyzing cmake logs ...")
    profiling_res = qibuild.cmake.profiling.parse_cmake_log(cmake_log, qibuild_dir)
    outdir = os.path.join(build_dir, "profile")
    qibuild.cmake.profiling.gen_annotations(profiling_res, outdir, qibuild_dir)
    ui.info(ui.green, "Annotations generated in", outdir)

def display_options(build_dir):
    """ Display the options by looking in the CMake cache

    """
    cache_path = os.path.join(build_dir, "CMakeCache.txt")
    print "-- Build options: "
    cache = read_cmake_cache(cache_path)
    opt_keys = [x for x in cache if x.startswith(("WITH_", "ENABLE_"))]
    if not opt_keys:
        print "  <no options found>"
        return
    opt_keys.sort()
    padding = max(len(x) for x in opt_keys) + 3
    for key in opt_keys:
        ui.info("  %s : %s" % (key.ljust(padding), cache[key]))

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

def get_cmake_qibuild_dir():
    """Get the path to cmake modules.

    First, look for a project named `qibuild` in the worktree, (if
    a ``worktree`` was passed,
    then, assume we are using qibuild from sources,
    then assume we are using an installed version of qibuild.
    """
    res = find_installed_cmake_qibuild_dir(qibuild.QIBUILD_ROOT_DIR)
    if not res:
        mess  = "Could not find qibuild cmake framework path\n"
        mess += "Please file a bug report with the details of your installation"
        qisys.error.Error(mess)
    return res

def find_installed_cmake_qibuild_dir(python_dir):
    ui.debug("looking for cmake code from", python_dir)
    for candidate in [
        # python in qibuild/python, cmake in qibuild/cmake
        ("..", "..", "cmake"),
        # python in lib/python-2.7/{dist,site}-packages,
        # cmake in share/cmake/
        # (default pip)
        ("..", "..", "..", "..", "share", "cmake"),
        # python in local/lib/python-2.7/{dist,site}-packages,
        # cmake in share/cmake
        # (debian's pip)
        ("..", "..", "..", "..", "..", "share", "cmake"),
        # python in Python27\Lib\{dist,site}-packages
        # cmake in Python27\share\cmake
        # (windows' pip)
        ("..", "..", "..", "share", "cmake"),
        # python in qibuild.egg/qibuild,
        # cmake in qibuild.egg/share/cmake
        # (pip with setuptools)
        ("..", "share", "cmake"),
        # pip on mac
        (sys.prefix, "share", "cmake")
        ]:

        rel_path = os.path.join(*candidate)
        res = os.path.join(python_dir, rel_path)
        res = qisys.sh.to_native_path(res)
        qibuild_config = os.path.join(res, "qibuild", "qibuild-config.cmake")
        ui.debug("trying", qibuild_config)
        if os.path.exists(qibuild_config):
            return res

def get_binutil(name, cmake_var=None, build_dir=None, env=None):
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
    if res and not res.endswith("-NOTFOUND"):
        return res
    return qisys.command.find_program(name, env=env)


def check_root_cmake_list(cmake_list_file):
    """ Check that the root CMakeLists is correct.

    * It should contain a cmake_minimum_required() line
    * It should contain a call to project()
    * If find_package(qibuild) is called, it should be
      called after project()

    """
    dirname = os.path.dirname(cmake_list_file)
    suggested_project_name = os.path.basename(dirname)
    message = ""
    lines = list()
    with open(cmake_list_file, "r") as fp:
        lines = fp.readlines()

    project_line_number = None
    find_qibuild_line_number = None
    minimum_required_found = False
    for (i, line) in enumerate(lines):
        if re.match(r'^\s*project\s*\(', line, re.IGNORECASE):
            project_line_number = i
        if re.match(r'^\s*find_package\s*\(.*qibuild\.*\)', line,
                    re.IGNORECASE):
            find_qibuild_line_number = i
        if re.match(r'^\s*cmake_minimum_required\(', line,
                    re.IGNORECASE):
            minimum_required_found = True

    if not minimum_required_found:
        message += """
* Missing call to cmake_minimum_required()
Add a line looking like:

cmake_minimum_required(VERSION 2.8)

At the top of the CMakeLists.txt file
"""

    if project_line_number is None:
        message += """
* Missing call to project().
Please fix this by editing the file so that it looks like

cmake_minimum_required(VERSION 2.8)
project({project_name})
find_package(qibuild)

""".format(
            project_name=suggested_project_name)

    if find_qibuild_line_number is not None and \
            project_line_number is not None and \
            project_line_number > find_qibuild_line_number:
        message += """
* The call to find_package(qibuild) should be AFTER the call to project()
"""
    if message:
        raise IncorrectCMakeLists(cmake_list_file, message)

class IncorrectCMakeLists(qisys.error.Error):
    def __init__(self, cmake_list_file, message):
        self.cmake_list_file = cmake_list_file
        self.message = message

    def __str__(self):
        message = "Invalid CMakeLists.txt file detected\n"
        message += "(in %s)\n" % self.cmake_list_file
        message += self.message
        return message
