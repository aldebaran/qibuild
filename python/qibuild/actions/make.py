## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Build a project

"""

from qisys import ui

import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("make options")
    group.add_argument("--rebuild", "-r", action="store_true", default=False)
    group.add_argument("--no-fix-shared-libs",  action="store_false",
                        dest="fix_shared_libs",
                        help="Do not try to fix shared libraries after build. "
                             "Used by `qibuild package`")
    group.add_argument("--verbose-make", action="store_true", default=False,
                       help="Set verbose for make. It will print the executed commands.")
    group.add_argument("--coverity", action="store_true", default=False,
                       help="Build using cov-build. Ensure you have "
                       "cov-analisys installed on your machine.")

@ui.timer("qibuild make")
def do(args):
    """Main entry point"""
    build_worktree = qibuild.parsers.get_build_worktree(args)
    build_projects = qibuild.parsers.get_build_projects(build_worktree, args)
    for i, build_project in enumerate(build_projects):
        ui.info_count(i, len(build_projects),
                      ui.blue, build_project.name)
        build_project.build(num_jobs=args.num_jobs, rebuild=args.rebuild,
                           fix_shared_libs=args.fix_shared_libs,
                           verbose_make=args.verbose_make, coverity=args.coverity)
