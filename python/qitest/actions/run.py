## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Launch automatic tests

"""

import argparse
import os
import sys

from qisys import ui
import qisys.parsers
import qibuild.test_runner
import qitest.parsers
import qitest.actions.list

def configure_parser(parser):
    """Configure parser for this action"""
    qisys.parsers.default_parser(parser)
    qitest.parsers.test_parser(parser)
    parser.add_argument("qitest_json", help="path to a qitest.json file")

def do(args):
    """Main entry point"""
    qitest_json = args.qitest_json
    test_project = TestProject(qitest_json)
    test_runner = qibuild.test_runner.ProjectTestRunner(test_project)
    test_runner.cwd = os.path.abspath(os.path.dirname(args.qitest_json))
    test_runner.pattern = args.pattern
    test_runner.perf = args.perf
    test_runner.coverage = args.coverage
    test_runner.valgrind = args.valgrind
    test_runner.verbose = args.verbose_tests
    test_runner.num_cpus = args.num_cpus
    test_runner.num_jobs = args.num_jobs
    test_runner.nightly = args.nightly
    res = test_runner.run()
    if not res:
        sys.exit(1)


class TestProject(object):
    """ A class to keep ProjectTestRunner happy """
    def __init__(self, qitest_json):
        self.qitest_json = qitest_json
        self.build_directory = os.path.dirname(qitest_json)
        self.sdk_directory = os.path.join(self.build_directory)
