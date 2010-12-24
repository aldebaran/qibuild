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
    group = parser.add_argument_group("cmake arguments")
    group.add_argument("-D", dest="cmake_flags", action="append", help="additional cmake flags")

def _print_list(name, elts):
    print ""
    print "%s:" % (name)
    for elt in elts:
        print " -", elt

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    #toc      = qibuild.toc.toc_open(args.work_tree, use_env=True)
    tob      = qibuild.toc.tob_open(args.work_tree, args, use_env=True)

    wanted_projects = qibuild.toc.get_projects_from_args(tob, args)
    #_print_list("project wanted", wanted_projects)

    (src_projects, bin_projects) = tob.split_sources_and_binaries(wanted_projects)
    #_print_list("binary projects", bin_projects)
    #_print_list("source projects", src_projects)

    for project in src_projects:
        logger.info("Bootstraping [%s]", project)
        dep_sdk_dirs = tob.get_sdk_dirs(project)
        qibuild.toc.bootstrap_project(tob.get_project(project), dep_sdk_dirs)

    for project in src_projects:
        logger.info("Configuring %s", tob.get_project(project))
        qibuild.toc.configure_project(tob.get_project(project), args.cmake_flags)

if __name__ == "__main__":
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])


