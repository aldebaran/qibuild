## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" This module contains the Project class, and method to
handle them

A project is simply a directory in a worktree containing a qibuild.manifest
file.

The :py:class:`toc` object is able to:
 * update a project to set cmake flags, build directory and so on
   (see :py:func:`update_project`
 * bootstrap the project to generate the dependencies.cmake used
   by the qibuild CMake framework
   (see :py:func:`bootstrap_project`)

To use the project build results, from an other project,
you just have to add sdk directory to CMAKE_FIND_ROOT_PATH

"""

import os

from qisys import ui
import qisys.sh
import qisys.qixml

import qibuild

def is_buildable(worktree_project):
    cmake_lists = os.path.join(worktree_project.path, "CMakeLists.txt")
    return os.path.exists(worktree_project.qiproject_xml) and os.path.exists(cmake_lists)

def build_projects(worktree):
    build_projects = [p for p in worktree.projects if is_buildable(p)]
    return build_projects

class Project:
    """ Store information about a :term:`project`

    """
    def __init__(self, toc, path):
        self.toc  = toc
        self.name = None
        self.path  = path
        self.depends    = list()
        self.rdepends   = list()
        self.config     = qibuild.config.ProjectConfig()

        #build related settings
        self.cmake_flags     = list()
        self._custom_sdk_dir = False

        self.load_config()

    @property
    def cmakecache_path(self):
        return os.path.join(self.build_directory, "CMakeCache.txt")

    @property
    def qiproject_xml(self):
        return os.path.join(self.path, "qiproject.xml")

    @property
    def build_directory(self):
        # Handle custom global build directory containing all projects
        bname = "build-%s" % self.toc.get_build_folder_name()

        singlebdir = self.toc.config.local.build.build_dir
        if singlebdir:
            singlebdir = os.path.expanduser(singlebdir)
            if not os.path.isabs(singlebdir):
                singlebdir = os.path.join(self.toc.worktree.root, singlebdir)
            bname = os.path.join(bname, self.name)
            return os.path.normpath(os.path.join(singlebdir, bname))

        return os.path.join(self.path, bname)

    @property
    def sdk_directory(self):
        if self._custom_sdk_dir:
            return self._custom_sdk_dir

        return os.path.join(self.build_directory, "sdk")

    def is_configured(self):
        return os.path.exists(self.cmakecache_path)

    def load_config(self):
        """ Update project dependency list """
        handle_old_manifest(self.path)
        if not os.path.exists(self.qiproject_xml):
            return
        self.config.read(self.qiproject_xml)
        self.name = self.config.name
        self.depends  = self.config.depends
        self.rdepends = self.config.rdepends

    def summarize_options(self):
        """ Display all the options coming from various WITH_*
        and ENABLE_* arguments

        """
        print "-- Build options: "
        cache = qibuild.cmake.read_cmake_cache(self.cmakecache_path)
        opt_keys = [x for x in cache if x.startswith(("WITH_", "ENABLE_"))]
        if not opt_keys:
            print "  <no options found>"
            return
        opt_keys.sort()
        padding = max(len(x) for x in opt_keys) + 3
        for key in opt_keys:
            print "  %s : %s" % (key.ljust(padding), cache[key])

    def __str__(self):
        res = ""
        res += "Project: %s\n" % (self.name)
        res += "  path            = %s\n" % self.path
        res += "  depends         = %s\n" % self.depends
        res += "  rdepends        = %s\n" % self.rdepends
        res += "  build_directory = %s\n" % self.build_directory
        res += "  cmake_flags     = %s"   % ", ".join(self.cmake_flags)
        return res

    def __repr__(self):
        res = "<Project %s in %s>" % (self.name, self.path)
        return res

def name_from_directory(project_dir):
    """Get the project name from the project directory

    The directory should contain a "qiproject.xml" file,
    looking like

        <project name="...">

        </project>

    If such a section can not be found, simply return
    the base name of the directory
    """
    # FIXME: qiproject.xml is read twice!
    # once for finding project names, and an other time for
    # loading complete configuration (with {r,}depends)
    handle_old_manifest(project_dir)
    xml = os.path.join(project_dir, "qiproject.xml")
    if not os.path.exists(xml):
        return os.path.basename(project_dir)
    p_cfg = qibuild.config.ProjectConfig()
    p_cfg.read(xml)
    return p_cfg.name


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
        ui.warning("Invalid version.cmake. Should have a line looking like\n"
           "set(%s_VERSION <VERSION>)" % up_name)
        return None
    return match.groups()[0]



def update_project(project, toc):
    """ Update a project using a Toc instance:

    This is to be called right after the toc object has
    been created, to be sure that the settings are consistent
    among all the projects.

    """
    # Handle single sdk dir
    sdk_dir = toc.config.local.build.sdk_dir
    if sdk_dir:
        if os.path.isabs(sdk_dir):
            project._custom_sdk_dir = sdk_dir
        else:
            project._custom_sdk_dir = os.path.join(toc.worktree.root, sdk_dir)
        bname = "sdk-%s" % (toc.get_build_folder_name())
        project._custom_sdk_dir = os.path.normpath(os.path.join(project._custom_sdk_dir, bname))
        cmake_sdk_dir = qisys.sh.to_posix_path(project.sdk_directory)
        project.cmake_flags.append("QI_SDK_DIR=%s" % (cmake_sdk_dir))

    # add CMAKE_BUILD_TYPE cmake flags
    if toc.build_type:
        project.cmake_flags.append("CMAKE_BUILD_TYPE=%s" % (toc.build_type))

    # add cmake flags
    if toc.user_cmake_flags:
        project.cmake_flags.extend(toc.user_cmake_flags)

    # add the toolchain file:
    if toc.toolchain is not None:
        tc_file = toc.toolchain.toolchain_file
        toolchain_path = qisys.sh.to_posix_path(tc_file)
        project.cmake_flags.append('CMAKE_TOOLCHAIN_FILE=%s' % toolchain_path)

    # lastly, add a correct -DCMAKE_MODULE_PATH
    cmake_qibuild_dir = qibuild.cmake.get_cmake_qibuild_dir()
    qibuild_dir = os.path.join(cmake_qibuild_dir, "qibuild")
    project.cmake_flags.append("qibuild_DIR=%s" % qibuild_dir)


def generate_path_conf(project, toc):
    """ generate build/sdk/share/qi/path.conf
    """

    towrite  = "# File autogenerated by qibuild configure based on\n"
    towrite += "# dependencies found in qiproject.xml\n"
    towrite += "\n"

    (_, projects) = qibuild.cmdparse.get_deps(toc, [project], runtime=True)
    dep_sdk_dirs = [x.sdk_directory for x in projects]

    for sdk_dir in dep_sdk_dirs:
        towrite += qisys.sh.to_posix_path(sdk_dir) + "\n"

    path_dconf = os.path.join(project.sdk_directory, "share", "qi")
    qisys.sh.mkdir(path_dconf, recursive=True)

    path_conf = os.path.join(path_dconf, "path.conf")
    with open(path_conf, "w") as fp:
        fp.write(towrite)


def bootstrap_project(project, toc):
    """ Create the magic build/dependencies.cmake file


    """
    generate_path_conf(project, toc)

    # To be written in dependencies.cmake
    to_write = """
#############################################
#QIBUILD AUTOGENERATED FILE. DO NOT EDIT.
#############################################

# Add path to CMake framework path if necessary:
set(_qibuild_path "{cmake_qibuild_dir}")
list(FIND CMAKE_MODULE_PATH "${{_qibuild_path}}" _found)
if(_found STREQUAL "-1")
  # Prefer cmake files matching  current qibuild installation
  # over cmake files in the cross-toolchain
  list(INSERT CMAKE_MODULE_PATH 0 "${{_qibuild_path}}")


  # Uncomment this if you really need to use qibuild
  # cmake files from the cross-toolchain
  # list(APPEND CMAKE_MODULE_PATH "${{_qibuild_path}}")
endif()

# Dependencies:
{dep_to_add}

# Store CMAKE_MODULE_PATH and CMAKE_FIND_ROOT_PATH in cache:
set(CMAKE_MODULE_PATH ${{CMAKE_MODULE_PATH}} CACHE INTERNAL ""  FORCE)
set(CMAKE_FIND_ROOT_PATH ${{CMAKE_FIND_ROOT_PATH}} CACHE INTERNAL ""  FORCE)

{custom_cmake_code}
"""
    custom_cmake_code = ""
    config = toc.active_config
    if toc.local_cmake:
        to_include = qisys.sh.to_posix_path(toc.local_cmake)
        custom_cmake_code += 'include("%s")\n' % to_include

    cmake_qibuild_dir = qibuild.cmake.get_cmake_qibuild_dir()
    cmake_qibuild_dir = qisys.sh.to_posix_path(cmake_qibuild_dir)
    dep_sdk_dirs = toc.get_sdk_dirs(project.name)

    dep_to_add = ""
    for sdk_dir in dep_sdk_dirs:

        dep_to_add += """
list(FIND CMAKE_FIND_ROOT_PATH "{sdk_dir}" _found)
if(_found STREQUAL "-1")
    list(INSERT CMAKE_FIND_ROOT_PATH 0 "{sdk_dir}")
endif()
""".format(sdk_dir=qisys.sh.to_posix_path(sdk_dir))

    to_write = to_write.format(
        cmake_qibuild_dir  = cmake_qibuild_dir,
        dep_to_add        = dep_to_add,
        custom_cmake_code = custom_cmake_code
    )

    qisys.sh.mkdir(project.build_directory, recursive=True)

    dep_cmake = os.path.join(project.build_directory, "dependencies.cmake")

    with open(dep_cmake, "w") as fp:
        fp.write(to_write)


def handle_old_manifest(directory):
    """ Handle processing a qibuild.manifest file,
    transforming it to a project.xml file on the fly

    """
    project_xml = os.path.join(directory, "qiproject.xml")
    if not os.path.exists(project_xml):
        qibuild_manifest = os.path.join(directory, "qibuild.manifest")
        if os.path.exists(qibuild_manifest):
            xml = qibuild.config.convert_project_manifest(qibuild_manifest)
            with open(project_xml, "w") as fp:
                fp.write(xml)

def project_from_dir(toc, directory=None, raises=True):
    """Return a project name from a directory.

    """
    if not directory:
        directory = os.getcwd()
    head = directory
    tail = None
    qiproj_xml = None
    while True:
        candidate = os.path.join(head, "qiproject.xml")
        if os.path.exists(candidate):
            qiproj_xml = candidate
            break
        (head, tail) = os.path.split(head)
        if not tail:
            break
    if not qiproj_xml:
        if raises:
            mess  = "Could not guess project name from current working directory: "
            mess += "'%s'\n" % os.getcwd()
            mess += "(No qiproject.xml found in the parent directories)\n"
            mess += "Please go inside a project, or specify the project name "
            mess += "from the command line"
            raise Exception(mess)
        else:
            return None
    xml_elem = qisys.qixml.read(qiproj_xml)
    project_name = xml_elem.getroot().get("name")
    if toc.get_project(project_name, raises=False):
        return project_name
    mess = """Found a valid qiproject.xml ('{qiproj_xml}')
while trying to guess a buildable project from the current working dir ('{cwd}')
But the project name: '{project_name}' does not match any buildable toc project"""
    mess = mess.format(qiproj_xml=qiproj_xml, cwd=directory, project_name=project_name)
    ui.warning(mess)
    project_path = os.path.dirname(qiproj_xml)
    res = add_missing_buildable_project(toc, project_name, project_path)
    return res


def add_missing_buildable_project(toc, project_name, project_path):
    """ Do something when we found a qiproject.xml
    but the project is not a buildable project

    Possible reasons:

      * we need to create a CMakeLists.txt file
      * we need to patch the qiproject.xml of a parent qibuild project
      * we need to add the project to worktree.xml instead

    If any case, ask the user before doing anything, but by default
    try our best so that the command can continue

    """
    check_parent_project(toc, project_name, project_path)
    check_worktree(toc, project_name, project_path)
    check_missing_cmake(project_path)
    return toc.get_project(project_name).name

def check_missing_cmake(project_path):
    """ Check if the qibuild project was not found because there
    there was a missing CMakeLists.txt file

    """
    cmake_lists = os.path.join(project_path, "CMakeLists.txt")
    if os.path.exists(cmake_lists):
        return
    mess = """The project in {project_path}
does not have a CMakeLists.txt file at the root.

If this is really supposed to be a buildable project, you can run
   `qibuild convert`  to create a CMakeLists.txt"""
    raise Exception(mess.format(project_path=project_path))

def check_parent_project(toc, project_name, project_path):
    """ Check if the qibuild project was not found because
    there was a missing
    <project src= ... />  in the parent qiproject.xml file

    """
    parent_proj = get_parent_project(toc, project_path)
    if not parent_proj:
        return
    parent_qiproj = os.path.join(parent_proj.path, "qiproject.xml")
    if not os.path.exists(parent_qiproj):
        return
    question = "Add the path to project %s to its parent qiproject.xml"
    question = question % (project_name)
    answer = qisys.interact.ask_yes_no(question, default=True)
    if answer:
        ui.info("Patching", parent_qiproj)
        tree = qisys.qixml.read(parent_qiproj)
        child_src = os.path.relpath(project_path, parent_proj.path)
        child_src = qisys.sh.to_posix_path(child_src)
        to_add = qisys.qixml.etree.Element("project")
        to_add.set("src", child_src)
        tree.getroot().append(to_add)
        qisys.qixml.write(tree, parent_qiproj)
        toc.projects = list()
        toc.worktree.load()
        toc.update_projects()

def check_worktree(toc, project_name, project_path):
    """ Check if the qibuild project was not found
    because the project source is not registered in the
    current worktree

    return True if the problem was fixed

    """
    wt_proj = toc.worktree.get_project(project_path, raises=False)
    if wt_proj:
        return
    question = "Add the path to the project %s to the worktree in %s"
    answer = qisys.interact.ask_yes_no(question % (project_name, toc.worktree.root),
                                         default=True)
    if answer:
        toc.worktree.add_project(project_path)
        toc.update_projects()

def get_parent_project(toc, directory):
    """Get the full path of a project using cwd."""
    head = os.path.dirname(directory)
    tail = None
    qiproj_xml = None
    while True:
        qiproj_xml = os.path.join(head, "qiproject.xml")
        if os.path.exists(qiproj_xml):
            break
        (head, tail) = os.path.split(head)
        if not tail:
            break
    if qiproj_xml:
        parent_path = os.path.dirname(qiproj_xml)
        return toc.worktree.get_project(parent_path, raises=False)
    else:
        return None

def is_build_dir(project, directory):
    """Check if directory can be a build dir of project."""
    parts = directory.split("-")
    if len(parts) == 0:
        return False

    if not parts.pop(0) == "build":
        return False

    is_build_dir1 = qibuild.toc.is_build_folder_name(parts,
                                               project.toc.worktree.qibuild_xml)
    is_build_dir2 = qibuild.toc.is_build_folder_name(parts,
                                                        project.toc.config_path)

    return is_build_dir1 or is_build_dir2
