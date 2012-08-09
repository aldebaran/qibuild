## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Build a project

"""

from qibuild import ui
import qibuild
import qibuild.cmdparse

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("make options")
    group.add_argument("-t", "--target", help="Special target to build")
    group.add_argument("--rebuild", "-r", action="store_true", default=False)
    group.add_argument("--no-fix-shared-libs",  action="store_false",
                        dest="fix_shared_libs",
                        help="Do not try to fix shared libraries after build. "
                             "Used by `qibuild package`")

def do(args):
    """Main entry point"""
    toc = qibuild.toc.toc_open(args.worktree, args)

    (project_names, _package_names, _not_found) = toc.resolve_deps()
    use_incredibuild = toc.config.build.incredibuild

    if toc.active_config:
        ui.info(ui.green, "Active configuration: ",
                ui.blue, "%s (%s)" % (toc.active_config, toc.build_type))
    projects = [toc.get_project(name) for name in project_names]

    project_count = len(projects)
    i = 0
    for project in projects:
        i += 1
        if args.target:
            mess = "Building target %s for" % args.target
        else:
            mess = "Building"
        ui.info(ui.green, "*", ui.reset, "(%i/%i)" % (i, project_count),
                ui.green, mess, ui.blue, project.name)
        toc.build_project(project, target=args.target, num_jobs=args.num_jobs,
                          incredibuild=use_incredibuild, rebuild=args.rebuild,
                          fix_shared_libs=args.fix_shared_libs)
