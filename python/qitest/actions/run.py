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
import qibuild.gcov
import qitest.parsers
import qitest.actions.list

def configure_parser(parser):
    """Configure parser for this action"""
    qitest.parsers.test_parser(parser)
    qibuild.parsers.project_parser(parser)
    qisys.parsers.build_parser(parser, include_worktree_parser=False)

def do(args):
    """Main entry point"""
    test_runner = qitest.parsers.get_test_runner(args)
    res = test_runner.run()
    if args.coverage:
        build_worktree = qibuild.parsers.get_build_worktree(args)
        build_project = qibuild.parsers.get_one_build_project(build_worktree, args)
        qibuild.gcov.generate_coverage_xml_report(build_project)
    if not res:
        sys.exit(1)
