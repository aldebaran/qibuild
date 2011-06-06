## Copyright (C) 2011 Aldebaran Robotics

"""Build a project

"""

import logging
import qibuild
import qibuild.cmdparse

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--target", help="Special target to build")
    parser.add_argument("--rebuild", "-r", action="store_true", default=False)

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc.toc_open(args.work_tree, args)

    (project_names, package_names, not_found) = qibuild.toc.resolve_deps(toc, args)
    use_incredibuild_str = toc.configstore.get("build.incredibuild",
        default="")

    if use_incredibuild_str.lower() in ["1", "true", "on", "yes"]:
        use_incredibuild = True
    else:
        use_incredibuild = False

    if toc.active_config:
        logger.info("Active configuration: %s", toc.active_config)

    for project_names in project_names:
        project = toc.get_project(project_names)
        if args.target:
            logger.info("Building target %s for project %s in %s",
                args.target, project.name, toc.build_folder_name)
        else:
            logger.info("Building %s in %s", project.name, toc.build_folder_name)
        toc.build_project(project, target=args.target, num_jobs=args.num_jobs,
            incredibuild=use_incredibuild, rebuild=args.rebuild)




