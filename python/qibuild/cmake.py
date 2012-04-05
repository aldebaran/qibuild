import os
import re
import subprocess
import logging

import qibuild.command
import qibuild.sh

LOGGER = logging.getLogger(__name__)

def get_known_cmake_generators():
    """ Get the list of known cmake generators.
    Assume cmake is in PATH, or path to cmake is correctly
    configured in ~/.config/qi/qibuild.xml

    """
    build_env = qibuild.config.get_build_env()
    cmake = qibuild.command.find_program("cmake", env=build_env)
    if not cmake:
        raise Exception("Could not find cmake executable\n"
          "Please install it if necessary and re-run `qibuild config --wizard`")
    process = subprocess.Popen([cmake, "--help"],
        stdout=subprocess.PIPE)
    (out, _err) = process.communicate()
    intersting = False
    intersting_lines = list()
    magic_line = "The following generators are available on this platform:"
    # pylint: disable-msg=E1103
    for line in out.splitlines():

        # handle lines like that:
        # Generator = "blalblalba"
        #       files.
        if len(line) >=3:
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
        qibuild.sh.rm(cache)

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
    qibuild.command.call(["cmake"] + cmake_args, cwd=build_dir, env=env)



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
find_package(qibuild)

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
    res = qibuild.sh.to_native_path(res)
    if os.path.isdir(res):
        return res

    # Then, assume we are in a toolchain or/in a SDK, with
    # the following layout sdk/share/cmake/qibuild, sdk/lib/python2.x/site-packages/qibuild
    sdk_dir = os.path.join(qibuild.QIBUILD_ROOT_DIR, "..",  "..", "..", "..")
    sdk_dir = qibuild.sh.to_native_path(sdk_dir)
    res = os.path.join(sdk_dir, "share", "cmake")
    if os.path.isdir(res):
        return res

    mess  = "Could not find qibuild cmake framework path\n"
    mess += "Please file a bug report with the details of your installation"
    raise Exception(mess)

