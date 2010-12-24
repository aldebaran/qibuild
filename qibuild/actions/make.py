##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""Configure a project

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

    (src_projects, bin_projects) = tob.split_sources_and_binaries(wanted_projects)

    for project in src_projects:
        logger.info("Building %s in %s", project, tob.build_folder_name)
        qibuild.toc.make_project(tob.get_project(project), tob.build_type)

if __name__ == "__main__":
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])


