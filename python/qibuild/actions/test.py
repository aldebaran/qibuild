## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Launch automatic tests
"""

import sys

import qisys
import qibuild
import qibuild.ctest
import qibuild.performance
import qibuild.gcov

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")
    parser.add_argument("-k", "--pattern", dest="pattern",
                        help="Filter tests matching this pattern")
    parser.add_argument("-l", "--list", dest="dry_run", action="store_true",
                        help="List what tests would be run")
    parser.add_argument("--slow", action="store_true",
                        help="Also run slow tests")
    parser.add_argument("-V", dest="verbose_tests", action="store_true",
                        help="display tests output")
    parser.add_argument("--valgrind", dest="valgrind", action="store_true",
                        help="run tests under valgrind")
    parser.add_argument("--nightmare", dest="nightmare", action="store_true",
                        help="run tests in shuffle and 20 times (apply only to gtest)")
    parser.add_argument("--test-args", dest="test_args",
                        help="Pass extra argument to test binary")
    parser.add_argument("--perf", dest="perf", action="store_true",
                        help="run perfs tests instead of pure tests.")
    parser.add_argument("--coverage", dest="coverage", action="store_true",
                        help="run coverage")
    parser.add_argument("--ncpu", dest="ncpu", default=-1, type=int,
                        help="set number of CPU each test is allowed to use (linux)")

    parser.set_defaults(slow=False)

def do(args):
    """Main entry point"""
    toc = qibuild.toc.toc_open(args.worktree, args)
    project = qibuild.cmdparse.project_from_args(toc, args)

    qibuild.toc.check_configure(toc, project)

    if args.perf:
        res = qibuild.performance.run_perfs(project,
                pattern=args.pattern,
                dry_run=args.dry_run)

    else:
        res = qibuild.ctest.run_tests(project, build_env=toc.build_env,
                pattern=args.pattern, slow=args.slow,
                dry_run=args.dry_run, valgrind=args.valgrind,
                verbose=args.verbose_tests, nightmare=args.nightmare,
                test_args=args.test_args, coverage=args.coverage,
                num_jobs=args.num_jobs, num_cpus=args.ncpu)
        if not res:
            sys.exit(1)
