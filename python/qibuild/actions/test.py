##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

""" launch automatic test
"""

import logging
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project_name", metavar="PROJECT")

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)

    project = toc.get_project(args.project_name)
    logger.info("Testing %s in %s", project.name, toc.build_folder_name)
    qibuild.ctest(project.directory, project.build_directory)



