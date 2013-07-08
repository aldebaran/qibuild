## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Package project using Maven.
"""

import sys
import os
import glob
import platform

from qisys import ui
import qimvn.package
import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--pom", required=False, dest="pom", help="pom xml project file")
    parser.add_argument("--skip-test", action="store_const", const="True", dest="skip_test", help="Skip JUnit test")

def do(args):
    """ Main entry point """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    projects = qibuild.parsers.get_build_projects(build_worktree, args, solve_deps=False)
    for project in projects:
        path = qimvn.package.package(project, pom_path=args.pom, skip_test=args.skip_test)
        ui.info(path)
