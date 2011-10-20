## Copyright (C) 2011 Aldebaran Robotics

import os
import logging

import qibuild.sh

LOGGER = logging.getLogger("qibuild.toc.project")

class Project:
    """ Store information about a project:
         - name
         - source directory
         - build directory
         - build configuration
         - dependencies
         - configstore (read from the qibuild.manifest file from the
                        source directory)
    """
    def __init__(self, name, directory):
        self.name            = name
        self.directory       = directory
        self.depends         = list()
        self.rdepends        = list()
        self.configstore     = qibuild.configstore.ConfigStore()

        #build related settings
        self.cmake_flags     = list()
        self.build_directory = None
        self.sdk_directory   = None
        self._custom_sdk_dir = False

        self.load_config()

    def get_sdk_dir(self):
        """ Return the SDK dir of the project.
        To use the project build results, from an other project,
        you just have to add this directory to CMAKE_PREFIX_PATH

        """
        return os.path.join(self.build_directory, "sdk")

    def load_config(self):
        """ Update project dependency list """
        qibuild_manifest = os.path.join(self.directory, "qibuild.manifest")
        self.configstore.read(qibuild_manifest)
        deps  = self.configstore.get("project.%s.depends"  % self.name, default="").split()
        rdeps = self.configstore.get("project.%s.rdepends" % self.name, default="").split()
        self.depends.extend(deps)
        self.rdepends.extend(rdeps)

    def set_custom_build_directory(self, build_dir):
        """ could be used to override the default build_directory
        """
        self.build_directory = build_dir

        #detect single sdk directory for multiple projects
        if not self._custom_sdk_dir:
            self.sdk_directory = os.path.join(self.build_directory, "sdk")


    def __str__(self):
        res = ""
        res += "Project: %s\n" % (self.name)
        res += "  directory       = %s\n" % self.directory
        res += "  depends         = %s\n" % self.depends
        res += "  rdepends        = %s\n" % self.rdepends
        res += "  build_directory = %s\n" % self.build_directory
        res += "  cmake_flags     = %s"   % ", ".join(self.cmake_flags)
        return res

def name_from_directory(project_dir):
    """Get the project name from the project directory

    The directory should contain a "qibuild.manifest" file,
    looking like

        [project foo]
        ...

    If such a section can not be found, simply return
    the base name of the directory
    """
    manifest = os.path.join(project_dir, "qibuild.manifest")
    if not os.path.exists(manifest):
        return os.path.basename(project_dir)
    config = qibuild.configstore.ConfigStore()
    conf_file = os.path.join(project_dir, "qibuild.manifest")
    config.read(conf_file)
    project_names = config.get("project", default=dict()).keys()
    if len(project_names) != 1:
        mess  = "The file %s is invalid\n" % conf_file
        mess += "It should contains exactly one project section"
        raise Exception(mess)

    return project_names[0]


def version_from_directory(project_dir):
    """Try to guess version from the sources of the project.

    Return None if not found.
    """
    version_cmake = os.path.join(project_dir, "version.cmake")
    if not os.path.exists(version_cmake):
        return None
    contents = None
    with open(version_cmake, "r") as fp:
        contents = fp.read()
    name = name_from_directory(project_dir)
    import re
    up_name = name.upper()
    match = re.match('^set\(%s_VERSION\s+"?(.*?)"?\s*\)' % up_name,
                     contents)
    if not match:
        LOGGER.warning("Invalid version.cmake. Should have a line looking like\n"
           "set(%s_VERSION <VERSION>)",  up_name)
        return None
    return match.groups()[0]



def update_project(project, toc):
    """ Update a project using a Toc instance:

    This will set:
        project.cmake_flags
        project.sdk_directory
        project.build_directory

    This is to be called right after the toc object has
    been created, to be sure that the settings are consistent
    among all the projects.

    """
    # Handle custom global build directory containing all projects
    singlebdir = toc.configstore.get("build.directory")
    if singlebdir:
        singlebdir = os.path.expanduser(singlebdir)
        if not os.path.isabs(singlebdir):
            singlebdir = os.path.join(toc.work_tree, singlebdir)
        bname = os.path.join("build-%s" % (toc.build_folder_name), project.name)
        project.build_directory = os.path.normpath(os.path.join(singlebdir, bname))
    else:
        bname = "build-%s" % (toc.build_folder_name)
        project.build_directory = os.path.join(project.directory, bname)


    # Handle single sdk dir
    sdk_dir = toc.configstore.get("build.sdk_dir", default=None)
    if sdk_dir:
        if os.path.isabs(sdk_dir):
            project.sdk_directory = sdk_dir
        else:
            project.sdk_directory = os.path.join(toc.work_tree, sdk_dir)
        bname = "sdk-%s" % (toc.build_folder_name)
        project.sdk_directory = os.path.normpath(os.path.join(project.sdk_directory, bname))
        project._custom_sdk_dir = True
        cmake_sdk_dir = qibuild.sh.to_posix_path(project.sdk_directory)
        project.cmake_flags.append("QI_SDK_DIR=%s" % (cmake_sdk_dir))
    else:
        #normal sdk dir in buildtree
        project.sdk_directory   = os.path.join(project.build_directory, "sdk")


    # add CMAKE_BUILD_TYPE cmake flags
    if toc.build_type:
        project.cmake_flags.append("CMAKE_BUILD_TYPE=%s" % (toc.build_type.upper()))

    # add cmake flags
    if toc.cmake_flags:
        project.cmake_flags.extend(toc.cmake_flags)



def bootstrap_project(project, toc):
    """ Create the magic build/dependencies.cmake file

    This is to be called right before calling cmake
    inside the project build directory, not before
    because we need to know about all the other projects
    inside the Toc oject to get the list of SDK dirs, for instance.
    """
    # To be written in dependencies.cmake
    to_write = """
#############################################
#QIBUILD AUTOGENERATED FILE. DO NOT EDIT.
#############################################

# Add path to CMake framework path if necessary:
set(_qibuild_path "{path_to_add}")
list(FIND CMAKE_MODULE_PATH "${{_qibuild_path}}" _found)
if(_found STREQUAL "-1")
  list(APPEND CMAKE_MODULE_PATH "${{_qibuild_path}}")
endif()

# Dependencies:
{dep_to_add}

# Store CMAKE_MODULE_PATH and  CMAKE_PREFIX_PATH in cache:
set(CMAKE_MODULE_PATH ${{CMAKE_MODULE_PATH}} CACHE INTERNAL ""  FORCE)
set(CMAKE_PREFIX_PATH ${{CMAKE_PREFIX_PATH}} CACHE INTERNAL ""  FORCE)

{custom_cmake_code}
"""
    custom_cmake_code = ""
    config = toc.active_config
    if config:
        global_dir = qibuild.configstore.get_config_dir()
        global_cmake = os.path.join(global_dir, "%s.cmake" % config)
        if os.path.exists(global_cmake):
            custom_cmake_code += 'include("%s")\n' % \
                qibuild.sh.to_posix_path(global_cmake)

        local_dir = os.path.join(toc.work_tree, ".qi")
        local_cmake = os.path.join(local_dir, "%s.cmake" % config)
        if os.path.exists(local_cmake):
            custom_cmake_code += 'include("%s")\n' % \
                qibuild.sh.to_posix_path(local_cmake)

    # This is cmake/qibuild, but we need to set the
    # cmake module_ath to cmake/ to be able to do
    # include(qibuild/general)
    cmake_qibuild_dir = qibuild.CMAKE_QIBUILD_DIR
    cmake_qibuild_dir = os.path.abspath(os.path.join(cmake_qibuild_dir, ".."))
    path_to_add = qibuild.sh.to_posix_path(cmake_qibuild_dir)

    dep_sdk_dirs = toc.get_sdk_dirs(project.name)

    dep_to_add = ""
    for sdk_dir in dep_sdk_dirs:
        dep_to_add += 'list(APPEND CMAKE_PREFIX_PATH "%s")\n' % \
            qibuild.sh.to_posix_path(sdk_dir)

    to_write = to_write.format(
        path_to_add       = path_to_add,
        dep_to_add        = dep_to_add,
        custom_cmake_code = custom_cmake_code
    )

    qibuild.sh.mkdir(project.build_directory, recursive=True)

    dep_cmake = os.path.join(project.build_directory, "dependencies.cmake")

    with open(dep_cmake, "w") as fp:
        fp.write(to_write)

