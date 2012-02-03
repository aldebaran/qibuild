## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Convert an existing project to a qiBuild project

"""

import os
import re
import sys
import difflib
import logging
from xml.etree import ElementTree as etree

import qibuild

LOGGER = logging.getLogger(__name__)

def guess_project_name(source_dir):
    """ Try to guess the project name

    """
    res = None
    qiproj_xml = os.path.join(source_dir, "qiproject.xml")
    res = name_from_xml(qiproj_xml)
    if res:
        return res
    qibuild_manifest = os.path.join(source_dir, "qibuild.manifest")
    res = name_from_cfg(qibuild_manifest)
    if res:
        return res
    base_cfg = os.path.join(source_dir, "base.cfg")
    res = name_from_cfg(base_cfg)
    if res:
        return res
    cmakelists = os.path.join(source_dir, "CMakeLists.txt")
    res = name_from_cmakelists(cmakelists)
    if res:
        return res
    res = os.path.basename(source_dir)
    return res

def name_from_xml(xml_path):
    """ Get a name from an qiproject.xml file

    """
    mess  = "Invalid qiproject.xml file detected!\n"
    mess += "(%s)\n" % xml_path
    if not os.path.exists(xml_path):
        return None
    tree = etree.ElementTree()
    try:
        tree.parse(xml_path)
    except Exception, e:
        mess += str(e)
        raise Exception(mess)

    # Read name
    root = tree.getroot()
    if root.tag != "project":
        mess += "Root node must be 'project'"
        raise Exception(mess)
    name = root.get('name')
    if not name:
        mess += "'project' node must have a 'name' attribute"
        raise Exception(mess)

    return name

def name_from_cfg(cfg_path):
    """ Get a name from a .cfg file

    """
    if not os.path.exists(cfg_path):
        return None
    config = qibuild.configstore.ConfigStore()
    config.read(cfg_path)
    projects = config.get("project")
    if not projects:
        return None
    if len(projects) == 1:
        return projects.keys()[0]

    for (name, project) in projects.iteritems():
        if project.get("depends"):
            return name

    return None

def name_from_cmakelists(cmakelists):
    """ Get a project name from a CMakeLists.txt file

    """
    if not os.path.exists(cmakelists):
        return None
    res = None
    regexp = re.compile(r'^\s*project\s*\((.*)\)', re.IGNORECASE)
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
    """ Fix the root CMakeLists.txt file

    If not found, create a new one
    If include(qibuild.cmake) is found, replace by find_package(qibuild)
    If include(boostrap.cmake) is found, replace by find_package(qibuild)

    If no find_package(qibuild) is found, add the line next to the
    first project() line

    """
    template = """# CMake file for {project_name}

cmake_minimum_required(VERSION 2.8)
project({project_name})
include(qibuild.cmake)

# qi_create_lib(...)

# qi_create_bin(...)

"""
    template = template.format(project_name=project_name)
    if not os.path.exists(cmakelists):
        with open(cmakelists, "w") as fp:
            fp.write(template)
            return

    with open(cmakelists, "r") as fp:
        old_lines = fp.readlines()

    new_lines = list()
    # Replace old include() by new find_package
    seen_find_package_qibuild = False
    for line in old_lines:
        match = re.match("\s*find_package\s*\(\s*qibuild\s*\)", line)
        if match:
            seen_find_package_qibuild = True
        match = re.match("\s*include\s*\(.*/?bootstrap.cmake.*", line)
        if match:
            if not seen_find_package_qibuild:
                new_lines.append('find_package(qibuild)\n')
                new_lines.append('include(qibuild/compat/compat)\n')
            seen_find_package_qibuild = True
        else:
            match = re.match("\s*include\s*\(.*/?qibuild.cmake.*", line)
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
            regexp = re.compile(r'^\s*project\s*\((.*)\)', re.IGNORECASE)
            if re.match(regexp, line):
                new_lines.append('find_package(qibuild)\n')
            new_lines.append(line)

    if dry_run:
        print "Would patch", cmakelists
        # Print a nice diff
        for line in difflib.unified_diff(old_lines, new_lines):
            sys.stdout.write(line)
        return

    with open(cmakelists, "w") as fp:
        print "Patching", cmakelists
        fp.writelines(new_lines)

def create_qiproj_xml(args):
    """ Create a new qiproject.xml

    """

    source_dir = args.source_dir
    project_name = args.project_name
    qiproj_xml = os.path.join(source_dir, "qiproject.xml")
    if os.path.exists(qiproj_xml):
        return

    # use convert_project_manifest() so that depends and other settings
    # are not lost
    for cfg_name in ["qibuild.manifest", "base.cfg"]:
        cfg_path = os.path.join(source_dir, cfg_name)
        if os.path.exists(cfg_path):
            xml = qibuild.config.convert_project_manifest(cfg_path)
            with open(qiproj_xml, "w") as fp:
                fp.write(xml)
            return

    proj_elem = etree.Element("project")
    proj_elem.set("name", project_name)
    tree = etree.ElementTree(element=proj_elem)
    if args.dry_run:
        print "Would create", qiproj_xml
        print "with: "
        print etree.tostring(proj_elem)
        return

    print "Creating", qiproj_xml
    tree.write(qiproj_xml)

def clean_up(args):
    """ Clean up old qibuild.cmake, boostrap.cmake, qibuild.manifest
    files

    """
    source_dir = args.source_dir
    names_to_remove = ["qibuild.cmake", "bootstrap.cmake", "qibuild.manifest"]
    for (root, _dirs, filenames) in os.walk(source_dir):
        for filename in filenames:
            if filename in names_to_remove:
                full_path = os.path.join(root, filename)
                if args.dry_run:
                    print "Would remove", full_path
                else:
                    print "Removing", full_path
                    qibuild.sh.rm(full_path)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
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
         "You won't be able to use the qibuild cmake frameowk")
    parser.set_defaults(dry_run=True, fix_cmake=True)

def do(args):
    """Main entry point """
    if not args.source_dir:
        args.source_dir = os.getcwd()
    args.source_dir = qibuild.sh.to_native_path(args.source_dir)

    if not args.project_name:
        args.project_name = guess_project_name(args.source_dir)
        LOGGER.info("Detected project name: %s", args.project_name)

    # Create qiproject.xml
    create_qiproj_xml(args)

    if not args.fix_cmake:
        return

    # Fix the root CMakeLists.txt:
    source_dir = args.source_dir
    project_name = args.project_name
    cmakelists = os.path.join(source_dir, "CMakeLists.txt")
    fix_root_cmake(cmakelists, project_name, dry_run=args.dry_run)

    # Remove useless files
    clean_up(args)

    if args.dry_run:
        LOGGER.info("Re-run with `qibuild convert --go` to proceed")
