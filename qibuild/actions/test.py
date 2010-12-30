##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

""" launch automatic test
"""

import os
import logging
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.shell.toc_parser(parser)
    qibuild.shell.build_parser(parser)
    qibuild.shell.project_parser(parser)

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    tob      = qibuild.toc.tob_open(args.work_tree, args, use_env=True)

    wanted_projects = qibuild.toc.get_projects_from_args(tob, args)
    (src_projects, bin_projects, not_found_projects) = tob.split_sources_and_binaries(wanted_projects)

    for project in src_projects:
        p = tob.get_project(project)
        logger.info("Testing %s in %s", project, tob.build_folder_name)
        logger.debug("%s", p)
        qibuild.build.ctest(p.directory, p.build_directory)

if __name__ == "__main__":
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])


