## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Launch automatic tests -- deprecated, use `qitest run` instead
"""

import argparse
import os
import sys

from qisys import ui
import qisys.script
import qibuild.parsers
import qitest.parsers
import qitest.actions.run

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    qitest.parsers.test_parser(parser, with_num_jobs=False)
    parser.set_defaults(num_jobs=1)
    parser.add_argument("-l", "--list", dest="list", action="store_true",
                        help="List what tests would be run")
    parser.add_argument("--slow", action="store_true", dest="nightly",
                        help=argparse.SUPPRESS)
    parser.add_argument("--build-first", action="store_true", help="rebuild first")


def do(args):
    """Main entry point"""
    if args.nightly:
        ui.warning("--slow option has no effect\n",
                   "Use `qibuild configure -DQI_WITH_NIGHTLY_TESTS=ON` instead")
    if args.nightmare:
        os.environ["GTEST_REPEAT"] = "20"
        os.environ["GTEST_SHUFFLE"] = "yes"

    if args.list:
        build_worktree = qibuild.parsers.get_build_worktree(args)
        project = qibuild.parsers.get_one_build_project(build_worktree, args)
        json = os.path.join(project.build_directory, "qitest.json")
        qisys.script.run_action("qitest.actions.list", [json])
        return

    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    deps_solver = cmake_builder.deps_solver
    if args.use_deps:
        dep_types = ["build"]
    else:
        dep_types = list()
    projects = deps_solver.get_dep_projects(cmake_builder.projects,
                                           dep_types)
    res = True
    for project in projects:
        if args.build_first:
            project.build()
        res = project.run_tests(**vars(args))

    if not res:
        sys.exit(1)
