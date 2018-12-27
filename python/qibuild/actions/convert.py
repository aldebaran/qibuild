#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Convert an existing project to a qiBuild project. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import re
import sys
import difflib
from xml.etree import ElementTree as etree

import qisys.parsers
from qisys import ui


def guess_project_name(source_dir):
    """ Try to guess the project name. """
    res = None
    qiproj_xml = os.path.join(source_dir, "qiproject.xml")
    res = name_from_xml(qiproj_xml)
    if res:
        return res
    cmakelists = os.path.join(source_dir, "CMakeLists.txt")
    res = name_from_cmakelists(cmakelists)
    if res:
        return res
    res = os.path.basename(source_dir)
    return res


def name_from_xml(xml_path):
    """ Get a name from an qiproject.xml file. """
    if not os.path.exists(xml_path):
        return None
    tree = etree.ElementTree()
    try:
        tree.parse(xml_path)
    except Exception as e:
        mess = "Invalid qiproject.xml file detected!\n"
        mess += "(%s)\n" % xml_path
        mess += str(e)
        raise Exception(mess)
    # Read name
    root = tree.getroot()
    if root.tag != "project":
        mess += "Root node must be 'project'"
        raise Exception(mess)
    if root.get("version") == "3":
        project_elem = root.find("qbuild")
        if not project_elem:
            return None
    else:
        project_elem = root
    name = project_elem.get('name')
    if not name:
        mess += "'project' node must have a 'name' attribute"
        raise Exception(mess)
    return name


def name_from_cmakelists(cmakelists):
    """ Get a project name from a CMakeLists.txt file. """
    if not os.path.exists(cmakelists):
        return None
    res = None
    # capture first word after project(), excluding quotes if any
    regexp = re.compile(r'^\s*project\s*\("?(\w+).*"?\)', re.IGNORECASE)
    lines = list()
    with open(cmakelists, "r") as fp:
        lines = fp.readlines()
    for line in lines:
        match = re.match(regexp, line)
        if match:
            res = match.groups()[0]
            res = res.strip()
            return res
    return res


def fix_root_cmake(cmakelists, project_name, dry_run=True):
    """
    Fix the root CMakeLists.txt file
    If not found, create a new one
    If include(qibuild.cmake) is found, replace by find_package(qibuild)
    If include(boostrap.cmake) is found, replace by find_package(qibuild)
    If no find_package(qibuild) is found, add the line next to the first project() line
    """
    template = """# CMake file for {project_name}

cmake_minimum_required(VERSION 2.8)
project({project_name})
find_package(qibuild)

# qi_create_lib(...)

# qi_create_bin(...)

"""
    template = template.format(project_name=project_name)
    if not os.path.exists(cmakelists):
        if not dry_run:
            with open(cmakelists, "w") as fp:
                fp.write(template)
        return
    with open(cmakelists, "r") as fp:
        old_lines = fp.readlines()
    fp.close()
    new_lines = list()
    # Replace old include() by new find_package
    seen_find_package_qibuild = False
    for line in old_lines:
        match = re.match(r"\s*find_package\s*\(\s*qibuild\s*\)", line)
        if match:
            seen_find_package_qibuild = True
        match = re.match(r"\s*include\s*\(.*/?bootstrap.cmake.*", line)
        if match:
            if not seen_find_package_qibuild:
                new_lines.append('find_package(qibuild)\n')
                new_lines.append('include(qibuild/compat/compat)\n')
            seen_find_package_qibuild = True
        else:
            match = re.match(r"\s*include\s*\(.*/?qibuild.cmake.*", line)
            if match:
                if not seen_find_package_qibuild:
                    new_lines.append('find_package(qibuild)\n')
                seen_find_package_qibuild = True
            else:
                new_lines.append(line)
    # Add find_package(qibuild) after project() if it is not there
    if not seen_find_package_qibuild:
        tmp_lines = new_lines[:]
        new_lines = list()
        for line in tmp_lines:
            new_lines.append(line)
            regexp = re.compile(r'^\s*project\s*\((.*)\)', re.IGNORECASE)
            if re.match(regexp, line):
                new_lines.append('find_package(qibuild)\n')
    if dry_run:
        ui.info("Would patch", cmakelists)
        # Print a nice diff
        for line in difflib.unified_diff(old_lines, new_lines):
            sys.stdout.write(line)
        return
    with open(cmakelists, "w") as fp:
        ui.info("Patching", cmakelists)
        fp.writelines(new_lines)
    fp.close()


def create_qiproj_xml(args):
    """ Create a new qiproject.xml. """
    source_dir = args.source_dir
    project_name = args.project_name
    qiproj_xml = os.path.join(source_dir, "qiproject.xml")
    if os.path.exists(qiproj_xml):
        return
    proj_elem = etree.Element("project")
    proj_elem.set("version", "3")
    tree = etree.ElementTree(element=proj_elem)
    qibuild_elem = etree.Element("qibuild")
    qibuild_elem.set("name", project_name)
    proj_elem.append(qibuild_elem)
    qisys.qixml.indent(proj_elem)
    if args.dry_run:
        ui.info("Would create", qiproj_xml, "\n"
                "with", "\n", etree.tostring(proj_elem))
        return
    ui.info("Creating", qiproj_xml)
    tree.write(qiproj_xml)


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.default_parser(parser)
    parser.add_argument("source_dir", nargs="?",
                        help="Top source directory of the project. "
                        "Defaults to current working directory.")
    parser.add_argument("--project-name",
                        dest="project_name",
                        help="Name of the project. Guess if not given")
    parser.add_argument("--go", action="store_false",
                        dest="dry_run",
                        help="Actually perform file changes")
    parser.add_argument("--dry-run", action="store_true",
                        dest="dry_run",
                        help="Only print what would be done. This is the default")
    parser.add_argument("--no-cmake", action="store_false",
                        dest="fix_cmake",
                        help="Do not touch any cmake file.\n"
                        "You won't be able to use the qibuild cmake framework")
    parser.set_defaults(dry_run=True, fix_cmake=True)


def do(args):
    """ Main entry point. """
    if not args.source_dir:
        args.source_dir = os.getcwd()
    args.source_dir = qisys.sh.to_native_path(args.source_dir)
    if not args.project_name:
        args.project_name = guess_project_name(args.source_dir)
        ui.info(ui.green, "Detected project name:", args.project_name)
    # Create qiproject.xml
    create_qiproj_xml(args)
    if not args.fix_cmake:
        return
    # Fix the root CMakeLists.txt:
    source_dir = args.source_dir
    project_name = args.project_name
    cmakelists = os.path.join(source_dir, "CMakeLists.txt")
    fix_root_cmake(cmakelists, project_name, dry_run=args.dry_run)
    if args.dry_run:
        ui.info(ui.green, "Re-run with `qibuild convert --go` to proceed")
