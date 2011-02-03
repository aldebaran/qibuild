##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

""" launch automatic test
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
        project_dir = qitools.qiworktree.search_manifest_directory(os.getcwd())
        project_name = os.path.basename(project_dir)
    else:
        project_name = args.project_name

    project = toc.get_project(project_name)
    logger.info("Testing %s in %s", project.name, toc.build_folder_name)
    qibuild.ctest(project.directory, project.build_directory)



