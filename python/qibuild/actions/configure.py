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
    qitools.argparsecommand.toc_parser(parser)
    qitools.argparsecommand.build_parser(parser)
    qitools.argparsecommand.project_parser(parser)
    group = parser.add_argument_group("cmake arguments")
    group.add_argument("--bootstrap", dest="bootstrap", action="store_true", help="only bootstrap projects, do not call cmake.")
    group.add_argument("--build-directory", dest="build_directory", action="store", help="override the default build directory used by cmake")
    group.add_argument("-D", dest="cmake_flags", action="append", help="additional cmake flags")

def do(args):
    """Main entry point"""
    if args.build_directory and not args.single:
        raise Exception("You should use --single when specifying a build directory")

    logger   = logging.getLogger(__name__)
    tob      = qibuild.toc.tob_open(args.work_tree, args, use_env=True)

    wanted_projects = qibuild.toc.get_projects_from_args(tob, args)
    (src_projects, bin_projects, not_found_projects) = tob.split_sources_and_binaries(wanted_projects)

    if args.build_directory:
        tob.get_project(wanted_projects[0]).set_custom_build_directory(args.build_directory)

    for project in src_projects:
        logger.info("Bootstraping [%s]", project)
        dep_sdk_dirs = tob.get_sdk_dirs(project)
        qibuild.toc.project.bootstrap(tob.get_project(project), dep_sdk_dirs)

    if args.bootstrap:
        return
    for project in src_projects:
        logger.info("Configuring %s in %s", project, tob.build_folder_name)
        logger.debug("%s", tob.get_project(project))
        qibuild.toc.project.configure(tob.get_project(project), args.cmake_flags)

if __name__ == "__main__":
    import sys
    qitools.argparsecommand.sub_command_main(sys.modules[__name__])


