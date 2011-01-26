##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

"""Configure a project

"""

import logging
import qibuild
import qitools.cmdparse

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--target", help="Special target to build")

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc.toc_open(args.work_tree, args, use_env=True)

    (project_names, package_names, not_found) = qibuild.toc.resolve_deps(toc, args)
    use_incredibuild_str = toc.configstore.get("general", "build", "incredibuild")
    if use_incredibuild_str.lower() in ["1", "true", "on", "yes"]:
        use_incredibuild = True
    else:
        use_incredibuild = False


    for project_names in project_names:
        project = toc.get_project(project_names)
        logger.info("Building %s in %s", project.name, toc.build_folder_name)
        toc.build_project(project, target=args.target, num_jobs=args.num_jobs,
            incredibuild=use_incredibuild)


if __name__ == "__main__":
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])


