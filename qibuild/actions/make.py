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

def _print_list(name, elts):
    print ""
    print "%s:" % (name)
    for elt in elts:
        print " -", elt

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc.toc_open(args.toc_work_tree, use_env=True, release=args.release)

    wanted_projects = qibuild.toc.get_projects_from_args(toc, args)
    _print_list("project wanted", wanted_projects)

    (src_projects, bin_projects) = qibuild.toc.dependencies.split_sources_and_binaries(wanted_projects, toc)
    _print_list("binary projects", bin_projects)
    _print_list("source projects", src_projects)

    for project in src_projects:
        logger.info("Building [%s]", project)
        qibuild.toc.make_project(toc.get_project(project))

if __name__ == "__main__":
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])


