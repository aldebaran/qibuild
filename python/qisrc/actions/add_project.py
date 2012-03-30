## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Add a project to a worktree

"""

import os

import qisrc
import qibuild

import qixml

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("src", metavar="PATH",
        help="Path to the project sources")
    parser.add_argument("--name",
        help="Name of the project")



def do(args):
    """Main entry point"""
    worktree = qibuild.open_worktree(args.worktree)
    project_src = args.src
    project_name = args.name
    if not project_name:
        # We need to find a project name to add it to the
        # worktree.
        qiproj_xml = os.path.join(project_src, "qiproject.xml")
        if os.path.exists(qiproj_xml):
            xml_tree = qixml.read(qiproj_xml)
            project_name = xml_tree.getroot().get("name")
        else:
            project_name = os.path.basename(project_src)
    worktree.add_project(project_name, project_src)
