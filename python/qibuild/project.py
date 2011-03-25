## Copyright (C) 2011 Aldebaran Robotics

import os
import shlex
import logging
import datetime

import qitools.sh

LOGGER = logging.getLogger("qibuild.toc.project")

class Project:
    """ Store information about a project:
         - name
         - source directory
         - build directory
         - build configuration
         - dependencies
    """
    def __init__(self, name, directory):
        self.name            = name
        self.directory       = directory
        self.depends         = list()
        self.rdepends        = list()

        #build related flags
        self.cmake_flags     = list()
        self.build_directory = None

    def get_sdk_dir(self):
        """ Return the SDK dir of the project.
        To use the project build results, from an other project,
        you just have to add this directory to CMAKE_PREFIX_PATH

        """
        return os.path.join(self.build_directory, "sdk")

    def update_depends(self, toc):
        """ Update project dependency list """
        deps  = toc.configstore.get("project", self.name, "depends", default="").split()
        rdeps = toc.configstore.get("project", self.name, "rdepends", default="").split()
        self.depends.extend(deps)
        self.rdepends.extend(rdeps)

    def update_build_config(self, toc, build_directory_name):
        """ Update cmake_flags
           - add flags from the build_config (read in toc's configstore)
           - add flags from the project config (read in toc's configstore project section)
           - add flags from the command line (stored in toc.cmake_flags when toc is built)
        """
        self.build_directory = os.path.join(self.directory, build_directory_name)

        build_config_flags = toc.configstore.get("general", "build", "cmake", "flags",
            default=None)
        if build_config_flags:
            self.cmake_flags.extend(shlex.split(build_config_flags))

        project_flags = toc.configstore.get("project", self.name, "cmake", "flags",
            default=None)
        if project_flags:
            self.cmake_flags.extend(shlex.split(project_flags))

        if toc.build_type:
            self.cmake_flags.append("CMAKE_BUILD_TYPE=%s" % (toc.build_type.upper()))

        if toc.toolchain.name != "system":
            # Used in qibuild/cmake
            self.cmake_flags.append("QI_TOOLCHAIN_NAME=%s" % (toc.toolchain.name))

        if toc.cmake_flags:
            self.cmake_flags.extend(toc.cmake_flags)

    def set_custom_build_directory(self, build_dir):
        """ could be used to override the default build_directory
        """
        self.build_directory = build_dir


    def get_package_name(self, continuous=False, version=None, arch=None):
        """Get the package name of a project.

        Recognized args are:
          continuous -> append the date the the name of the package
          version    -> if not given, will try to use version.cmake at
                        the root of the project
          arch       -> if not given, do nothing, else add this at the end
                        of the package name
        """
        res = [self.name]

        if not version:
            version = self.get_version()
            if version:
                res.append(version)
        else:
            res.append(version)

        if continuous:
            now = datetime.datetime.now()
            res.append(now.strftime("%Y-%m-%d"))

        if arch:
            res.append(arch)

        return "-".join(res)


    def get_version(self):
        """Try to guess version from the sources of the project.
        Return None

        """
        version_cmake = os.path.join(self.directory, "version.cmake")
        if not os.path.exists(version_cmake):
            return None
        contents = None
        with open(version_cmake, "r") as fp:
            contents = fp.read()

        import re
        up_name = self.name.upper()
        match = re.match('^set\(%s_VERSION\s+"?(.*?)"?\s*\)' % up_name,
                         contents)
        if not match:
            LOGGER.warning("Invalid version.cmake. Should have a line looking like\n"
               "set(%s_VERSION <VERSION>)",  up_name)
            return None
        return match.groups()[0]

    def __str__(self):
        res = ""
        res += "Project: %s\n" % (self.name)
        res += "  directory       = %s\n" % self.directory
        res += "  depends         = %s\n" % self.depends
        res += "  rdepends        = %s\n" % self.rdepends
        res += "  cmake_flags     = %s\n" % self.cmake_flags
        res += "  build_directory = %s" % self.build_directory
        return res


def get_qibuild_cmake_framework_path():
    """ return the path to the qiBuild Cmake framework """
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "cmake"))
    return qitools.sh.to_posix_path(path)

def bootstrap(project, dep_sdk_dirs):
    """Generate the find_deps.cmake for the given project
    """
    build_dir = project.build_directory
    qitools.sh.mkdir(build_dir)

    to_write  = "#############################################\n"
    to_write += "#QIBUILD AUTOGENERATED FILE. DO NOT EDIT.\n"
    to_write += "#############################################\n"
    to_write += "\n"
    to_write += "#QIBUILD CMAKE FRAMEWORK PATH:\n"
    to_write += "list(APPEND CMAKE_MODULE_PATH \"%s\")\n" % get_qibuild_cmake_framework_path()
    to_write += "\n"
    to_write += "#DEPENDENCIES:\n"
    for dep_sdk_dir in dep_sdk_dirs:
        to_write += "list(APPEND CMAKE_PREFIX_PATH \"%s\")\n" % qitools.sh.to_posix_path(dep_sdk_dir)
    to_write += "set(CMAKE_MODULE_PATH \"${CMAKE_MODULE_PATH}\" CACHE INTERNAL \"\" FORCE)\n"
    to_write += "set(CMAKE_PREFIX_PATH \"${CMAKE_PREFIX_PATH}\" CACHE INTERNAL \"\" FORCE)\n"

    output_path = os.path.join(build_dir, "dependencies.cmake")
    with open(output_path, "w") as output_file:
        output_file.write(to_write)
    LOGGER.debug("Wrote %s", output_path)
