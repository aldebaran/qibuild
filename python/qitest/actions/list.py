## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" List the tests"""


import os
import sys
from qisys import ui

import qisys.parsers
import qitest.conf
import qibuild.parsers

def configure_parser(parser):
    qitest.parsers.test_parser(parser)
    qibuild.parsers.project_parser(parser)
    qisys.parsers.build_parser(parser, include_worktree_parser=False)

def do(args):
    test_runners = qitest.parsers.get_test_runners(args)
    for test_runner in test_runners:
        ui.info("Tests in ", test_runner.project.sdk_directory)
        for i, test in enumerate(test_runner.tests):
            ui.info_count(i, len(test_runner.tests), test["name"])
