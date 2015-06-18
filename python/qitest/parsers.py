## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Collection of parser fonctions for qitests actions
"""

import copy
import os

from qisys import ui
import qisys.parsers
import qibuild.parsers
import qitest.project

def test_parser(parser, with_num_jobs=True):
    qisys.parsers.worktree_parser(parser)
    group = parser.add_argument_group("test options")
    group.add_argument("--perf", dest="perf", action="store_true",
                        help="run perfs tests instead of pure tests.")
    group.add_argument("-k", "--pattern", dest="patterns", action="append",
                        help="Filter tests matching these patterns")
    group.add_argument("-V", dest="verbose_tests", action="store_true",
                        help="display tests output")
    group.add_argument("--valgrind", dest="valgrind", action="store_true",
                        help="run tests under valgrind")
    group.add_argument("--nightmare", dest="nightmare", action="store_true",
                        help="run tests in shuffle and 20 times (apply only to gtest)")
    group.add_argument("--coverage", dest="coverage", action="store_true",
                        help="run coverage")
    group.add_argument("--ncpu", dest="num_cpus", default=-1, type=int,
                        help="set number of CPU each test is allowed to use (linux)")
    group.add_argument("--nightly", action="store_true", dest="nightly")
    group.add_argument("--break-on-failure", action="store_true", dest="break_on_failure",
                      help="Break on failure (for gtest only)")
    group.add_argument("--qitest-json", dest="qitest_jsons", action="append")
    group.add_argument("--root-output-dir", dest="root_output_dir",
                      help="Generate XML reports in the given directory " + \
                           "(instead of build/sdk/test-results)")

    parser.set_defaults(nightly=False)
    if with_num_jobs:
        group.add_argument("-j", dest="num_jobs", default=1, type=int,
                            help="Number of tests to run in parallel")
    return group

def get_test_runner(args, build_project=None, qitest_json=None):
    test_project = None
    if not qitest_json:
        qitest_json = vars(args).get("qitest_json")
    if not qitest_json:
        candidate = os.path.join(os.getcwd(), "qitest.json")
        if os.path.exists(candidate):
            qitest_json = candidate
    if qitest_json:
        test_project = qitest.project.TestProject(qitest_json)
    if not test_project:
        if build_project:
            test_project = build_project.to_test_project()

    if args.coverage and not build_project:
        raise Exception("""\
--coverage can only be used from a qibuild CMake project
""")

    if not test_project:
        return

    test_runner = qibuild.test_runner.ProjectTestRunner(test_project)
    if build_project:
        test_runner.cwd = build_project.sdk_directory
        test_runner.env = build_project.build_worktree.get_env()
    else:
        test_runner.cwd = os.path.dirname(qitest_json)

    test_runner.patterns = args.patterns
    test_runner.perf = args.perf
    test_runner.coverage = args.coverage
    test_runner.break_on_failure = args.break_on_failure
    test_runner.valgrind = args.valgrind
    test_runner.verbose = args.verbose_tests
    test_runner.num_cpus = args.num_cpus
    test_runner.num_jobs = args.num_jobs
    test_runner.nightly = args.nightly
    test_runner.nightmare = args.nightmare
    test_runner.root_output_dir = args.root_output_dir

    return test_runner

def get_test_runners(args):
    res = list()
    qitest_jsons = args.qitest_jsons or list()

    # first case: qitest.json in current working directory
    test_runner = get_test_runner(args)
    if test_runner:
        res.append(test_runner)

    # second case: qitest.json specified with --qitest-json
    for qitest_json in qitest_jsons:
        test_runner = get_test_runner(args, qitest_json=qitest_json)
        res.append(test_runner)

    # third case: parsing build projects
    try:
        build_worktree = qibuild.parsers.get_build_worktree(args)
        solve_deps = False
        if args.use_deps:
            solve_deps = True
        build_projects = qibuild.parsers.get_build_projects(
                build_worktree,
                args, solve_deps=solve_deps)
        for build_project in build_projects:
            test_runner = None
            try:
                test_runner = get_test_runner(args, build_project=build_project)
            except qibuild.project.NoQiTestJson:
                pass
            if test_runner:
                # avoid appending a test_runner guessed from a build project
                # when res already contains a test runner computed from a
                # --qitest-json argument
                known_cwds = [x.cwd for x in res]
                if not test_runner.cwd in known_cwds:
                    res.append(test_runner)
    except (qisys.worktree.NotInWorkTree, qibuild.parsers.CouldNotGuessProjectName):
        pass

    if not res:
        raise Exception("Nothing found to test")
    return res
