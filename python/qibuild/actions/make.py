## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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

    (project_names, _package_names, _not_found) = toc.resolve_deps()
    use_incredibuild = toc.config.build.incredibuild

    if toc.active_config:
        logger.info("Active configuration: %s (%s)", toc.active_config, toc.build_type)

    for project_names in project_names:
        project = toc.get_project(project_names)
        if args.target:
            logger.info("Building target %s for project %s in %s (%s)",
                args.target, project.name, toc.build_folder_name, toc.build_type)
        else:
            logger.info("Building %s in %s (%s)", project.name, toc.build_folder_name, toc.build_type)
        toc.build_project(project, target=args.target, num_jobs=args.num_jobs,
            incredibuild=use_incredibuild, rebuild=args.rebuild)




