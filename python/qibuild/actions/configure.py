##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

"""Configure a project

"""

import os
import logging
import qibuild
import qitools

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("cmake arguments")
    group.add_argument("--bootstrap", dest="bootstrap", action="store_true", help="only bootstrap projects, do not call cmake.")
    group.add_argument("--build-directory", dest="build_directory", action="store", help="override the default build directory used by cmake")
    group.add_argument("-D", dest="cmake_flags", action="append", help="additional cmake flags")

def do(args):
    """Main entry point"""
    if args.build_directory and not args.single:
        raise Exception("You should use --single when specifying a build directory")

    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc.open(args.work_tree, args, use_env=True)

    wanted_projects = qibuild.toc.get_projects_from_args(toc, args)
    (src_projects, bin_projects, not_found_projects) = toc.split_sources_and_binaries(wanted_projects)

    if args.build_directory:
        toc.projects[wanted_projects[0]].set_custom_build_directory(args.build_directory)

    for project in src_projects:
        logger.info("Bootstraping [%s]", project)
        dep_sdk_dirs = toc.get_sdk_dirs(project)
        qibuild.project.bootstrap(toc.projects[project], dep_sdk_dirs)

    from_conf = toc.configstore.get("general", "build", "cmake_generator")
    if from_conf and not args.cmake_generator:
        args.cmake_generator = from_conf

    if args.bootstrap:
        return
    for project in src_projects:
        logger.info("Configuring %s in %s", project, toc.build_folder_name)
        logger.debug("%s", toc.projects[project])
        qibuild.project.configure(toc.projects[project],
            generator=args.cmake_generator,
            flags=args.cmake_flags)

if __name__ == "__main__":
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])


