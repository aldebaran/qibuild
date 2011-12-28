""" Convert an existing project to a qiBuild project

"""

## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import re
import sys
import logging
import shutil

import qibuild

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
    parser.add_argument("source_dir", nargs="?",
        help="Top source directory of the project. "
             "Defaults to current working directory.")
    parser.add_argument("--no-cmake", action="store_false",
        dest="patch_cmake",
        help="Do not patch any cmake code. "
             "Use this if you do not want to depend on the qibuild "
             "CMake framework.")
    parser.set_defaults(cmake_patch=True)

def copy_qibuild(source_dir):
    """ Every convert function should at least call this

    """
    qibuild_template = os.path.join(qibuild.CMAKE_QIBUILD_DIR, "templates", "qibuild.cmake")
    shutil.copy(qibuild_template, os.path.join(source_dir, "qibuild.cmake"))

def create_qibuild_manifest(source_dir, project_name=None):
    """ Every convert function should at least call this.

    The project name will be the basename of the source_dir,
    unless project_name is not None.
    (the convert function may be able to guess the project name
    using a better way)

    """
    to_write = os.path.join(source_dir, "qibuild.manifest")
    if os.path.exists(to_write):
        LOGGER.info("%s already exists, nothing to do ;)",
            to_write)
        return

    if project_name is None:
        project_name = os.path.basename(source_dir)

    from qibuild import QIBUILD_ROOT_DIR
    manifest_in = os.path.join(QIBUILD_ROOT_DIR,
        "templates", "project", "qibuild.manifest")
    old_contents = ""
    with open(manifest_in, "r") as old_file:
        old_contents = old_file.read()
    new_contents = old_contents.replace("@project_name@", project_name)
    with open(to_write, "w") as new_file:
        new_file.write(new_contents)

def guess_type(source_dir):
    """ Try to guess the build system used by the sources.

    Return None if nothing seems to fit.
    """
    bootstrap = os.path.join(source_dir, "bootstrap.cmake")
    if os.path.exists(bootstrap):
        return "bootstrap"
    cmake = os.path.join(source_dir, "CMakeLists.txt")
    if os.path.exists(cmake):
        return "cmake"

    return None

def convert_bootstrap(source_dir, args):
    """ Convert a old bootstrap project to a qiBuild project

    """
    from qibuild import CMAKE_QIBUILD_DIR
    # Copy the qibuild.cmake file
    copy_qibuild(source_dir)

    # update the "bootstrap.cmake" files so that they try to include qibuild.cmake
    new_bootstrap = os.path.join(CMAKE_QIBUILD_DIR, "templates", "bootstrap.cmake")
    for (root, _dirs, filenames) in os.walk(source_dir):
        for filename in filenames:
            if filename == "bootstrap.cmake":
                full_path = os.path.join(root, filename)
                if args.patch_cmake:
                    LOGGER.debug("updating %s", full_path)
                    shutil.copy(new_bootstrap, full_path)

    # qibuild.manifest was once named base.cfg:
    project_name = None
    base_cfg = os.path.join(source_dir, "base.cfg")
    if os.path.exists(base_cfg):
        project_name = _name_from_base_cfg(base_cfg)

    create_qibuild_manifest(source_dir, project_name=project_name)


def _name_from_base_cfg(base_cfg):
    """ Convert an old base.cfg file to a new qibuild.manifest file

    """
    config = qibuild.configstore.ConfigStore()
    config.read(base_cfg)
    projects = config.get("project")
    if not projects:
        return None
    if len(projects) == 1:
        return projects.keys()[0]

    for (name, project) in projects.iteritems():
        if project.get("depends"):
            return name

    return None


def convert_cmake(source_dir, args):
    """ Patch the root's CMakeLists file, then
    add the missing qibuild.cmake and qibuild.manifest
    files

    """
    project_name = None
    root_cmake = os.path.join(source_dir, "CMakeLists.txt")
    lines = list()
    with open(root_cmake, "r") as fp:
        lines = fp.readlines()
    new_lines = list()
    regexp = re.compile(r'^\s*project\s*\((.*)\)', re.IGNORECASE)
    to_add = "include(qibuild.cmake)"
    qibuild_included = False
    for line in lines:
        new_lines.append(line)
        match = re.match(regexp, line)
        if match:
            new_lines.append(to_add + "\n")
            project_name = match.groups()[0]
            project_name = project_name.strip()
        match = re.match("\s*include\s*\(.*/?qibuild.cmake.*", line)
        if match:
            qibuild_included = True
    if args.patch_cmake and not qibuild_included:
        with open(root_cmake, "w") as fp:
            fp.writelines(new_lines)
        copy_qibuild(source_dir)

    create_qibuild_manifest(source_dir, project_name)

def convert_default(source_dir, args_):
    """ Create an empty CMakeLists, and assume project name
    if the basename of the source_dir

    """
    root_cmake = os.path.join(source_dir, "CMakeLists.txt")
    template = """# CMake file for {project_name}

cmake_minimum_required(VERSION 2.8)
project({project_name})
include(qibuild.cmake)

# qi_create_lib(...)

# qi_create_bin(...)

"""

    project_name = os.path.basename(source_dir)
    to_write = template.format(project_name=project_name)

    with open(root_cmake, "w") as fp:
        fp.write(to_write)

    copy_qibuild(source_dir)
    create_qibuild_manifest(source_dir)


def do(args):
    """Main entry point """
    source_dir = args.source_dir
    if not source_dir:
        source_dir = os.getcwd()
    source_dir = qibuild.sh.to_native_path(source_dir)

    source_type = guess_type(source_dir)

    if not source_type:
        LOGGER.warning("Could not guess type of the project, creating a new default cmake project")
        source_type = "default"

    this_module = sys.modules[__name__]
    fun_name = "convert_" + source_type
    convert_fun = None
    try:
        convert_fun = getattr(this_module, fun_name)
    except AttributeError:
        LOGGER.error("No method named %s, aborting", fun_name)
        return

    LOGGER.info("Converting %s from %s to qiBuild", source_dir, source_type)
    convert_fun(source_dir, args)

    LOGGER.info("Done. \n"
        "Create a qiBuild worktree if you have not already done so\n"
        "and try using `qibuild configure' now")


