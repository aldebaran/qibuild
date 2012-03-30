## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Launch automatic tests
"""

import logging
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")
    parser.add_argument("--test-name")

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc_open(args.worktree, args)

    if not args.project:
        project_name = qibuild.worktree.project_from_cwd()
    else:
        project_name = args.project

    project = toc.get_project(project_name)
    logger.info("Testing %s in %s", project.name, toc.build_folder_name)
    toc.test_project(project, test_name=args.test_name)

