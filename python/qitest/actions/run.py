## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
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
    test_runners = qitest.parsers.get_test_runners(args)
    global_res = True
    n = len(test_runners)
    for i, test_runner in enumerate(test_runners):
        if n != 1:
            ui.info(ui.bold, "::", "[%i on %i]" % (i + 1, len(test_runners)),
                    ui.reset, "Running tests in", ui.blue, test_runner.cwd)
        res = test_runner.run()
        if args.coverage:
            build_worktree = qibuild.parsers.get_build_worktree(args, verbose=False)
            build_project = qibuild.parsers.get_one_build_project(build_worktree, args)
            qibuild.gcov.generate_coverage_reports(build_project, output_dir=args.coverage_output_dir)
        global_res = global_res and res
    if not global_res:
        sys.exit(1)
