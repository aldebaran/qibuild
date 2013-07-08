## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Find an runable jar in target/ projects directories.
"""

import sys
import os
import glob
import platform

from qisys import ui
import qimvn.find
import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--cflags",
                        help="Outputs required compiler flags")
    parser.add_argument("--libs",
                        help="Ouputs required linnker flags")
    parser.add_argument("--cmake", dest="cmake", action="store_true",
                        help="Search in cmake cache")
    parser.add_argument("package")

def do(args):
    """ Main entry point """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    projects = build_worktree.build_projects
    path = qimvn.find.find(projects, args.package)
    ui.info(path)
