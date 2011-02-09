## Copyright (C) 2011 Aldebaran Robotics

""" Launch automatic tests
"""

import os
import logging
import qitools
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)

    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project

    project = toc.get_project(project_name)
    logger.info("Testing %s in %s", project.name, toc.build_folder_name)
    toc.test_project(project)



