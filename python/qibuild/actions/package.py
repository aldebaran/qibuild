## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a binary package, ready to be added in a toolchain """

import os
import sys

from qisys.qixml import etree
from qisys import ui
import qisys.sh
import qisys.archive
import qibuild.parsers


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("package options")

def do(args):
    """Main entry point"""
    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    projects = cmake_builder.projects
    if len(projects) != 1:
        raise Exception("This action can only work on one project")
    project = projects[0]

    archive_name = project.name
    version = project.version
    if not version:
        project.version = "0.1"

    build_dir_name = os.path.basename(project.build_directory)
    archive_suffix = build_dir_name.replace("build-", "")
    archive_name += "-" + version
    archive_name += "-" + archive_suffix

    destdir = os.path.join(cmake_builder.build_worktree.root, "package")
    destdir = os.path.join(destdir, archive_name)

    # Clean the destdir just in case the package was already generated
    qisys.sh.rm(destdir)

    build_type = cmake_builder.build_config.build_type
    if sys.platform.startswith("win") and build_type == "Release":
        _do_package(cmake_builder, destdir, build_type="Debug")
    _do_package(cmake_builder, destdir, build_type=build_type)

    package_xml_path = os.path.join(destdir, "package.xml")
    project.gen_package_xml(package_xml_path)

    ui.info(ui.blue, "::", ui.reset, ui.bold, "Compressing package ...")
    archive = qisys.archive.compress(destdir,
                                     algo="zip", quiet=True, flat=True,
                                     output=destdir + ".zip")

    # Clean up after ourselves
    qisys.sh.rm(destdir)
    ui.info(ui.green, "Package generated in", ui.reset, ui.bold, archive)
    return archive


def _do_package(cmake_builder, destdir, build_type="Release"):
    """ Helper function. On linux and mac this is only called
    once.

    On Windows this is called twice, both in debug and release
    This is because usually debug and release version of a library
    are incompatible on Windows.

    """
    cmake_builder.build_config.build_type = build_type

    cmake_builder.dep_types = ["build"]
    ui.info(ui.blue, "::", ui.reset, ui.bold, "Configuring ... (%s)" % build_type)
    cmake_builder.configure()
    ui.info(ui.blue, "::", ui.reset, ui.bold, "Building    ... (%s)" % build_type)
    cmake_builder.build()
    cmake_builder.dep_types = list()
    ui.info(ui.blue, "::", ui.reset, ui.bold, "Installing  ... (%s)" % build_type)
    cmake_builder.install(destdir)


def get_package_name(project, version=None, config=None):
    """Get the package name of a project.

    """
    res = [project.name]
    if version:
        res.append(version)
    if config:
        res.append(config)
    return "-".join(res)
