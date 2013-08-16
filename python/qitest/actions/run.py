## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Launch automatic tests

"""

import argparse
import sys

from qisys import ui
import qibuild.parsers
import qitest.actions.list

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("qitest run options")
    group.add_argument("-l", "--list", dest="list", action="store_true",
                        help="Deprectated - List what tests would be run\n"
                             "Use `qitest list` instead")
    # FIXME: supress from help instead
    group.add_argument("--slow", action="store_true", dest="nightly",
                        help="Deprecated - Do not use")
    group.add_argument("--perf", dest="perf", action="store_true",
                        help="run perfs tests instead of pure tests.")
    group.add_argument("-k", "--pattern", dest="pattern",
                        help="Filter tests matching this pattern")
    group.add_argument("-V", dest="verbose_tests", action="store_true",
                        help="display tests output")
    group.add_argument("--valgrind", dest="valgrind", action="store_true",
                        help="run tests under valgrind")
    group.add_argument("--nightmare", dest="nightmare", action="store_true",
                        help="run tests in shuffle and 20 times (apply only to gtest)")
    group.add_argument("--test-args", dest="test_args",
                        help="Pass extra argument to test binary")
    group.add_argument("--coverage", dest="coverage", action="store_true",
                        help="run coverage")
    group.add_argument("--ncpu", dest="num_cpus", default=-1, type=int,
                        help="set number of CPU each test is allowed to use (linux)")
    group.add_argument("--build-first", action="store_true", help="rebuild first")

def do(args):
    """Main entry point"""
    if args.list:
        qitest.actions.list.do(args)
        return

    if args.nightly:
        ui.warning("--slow option has no effect\n",
                   "Use `qibuild configure -DQI_WITH_NIGHTLY_TESTS=ON` instead")

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
        res, message = project.run_tests(**vars(args))
        ui.info(*message)

    if not res:
        sys.exit(1)

