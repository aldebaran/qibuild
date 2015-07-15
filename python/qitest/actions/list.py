## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" List the tests"""

import os
import re
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

    # rule to check for tests which doesn't follow naming convention
    warn_name_count = 0
    warn_type_count = 0
    expr = re.compile("^test_.*")
    for test_runner in test_runners:
        ui.info("Tests in ", test_runner.project.sdk_directory)
        for i, test in enumerate(test_runner.tests):
            name = test["name"]
            if expr.match(name):
                if test.get("gtest") or test.get("pytest"):
                    ui.info_count(i, len(test_runner.tests), name)
                else:
                    msg = "(%i/%i) type warning: %s" % (i, len(test_runner.tests), name)
                    ui.info(ui.red, "*", ui.yellow, msg)
                    warn_type_count = warn_type_count + 1
            else:
                msg = "(%i/%i) name warning: %s" % (i, len(test_runner.tests), name)
                ui.info(ui.red, "*", ui.yellow, msg)
                warn_name_count = warn_name_count + 1
    if warn_name_count:
        msg = "(%i/%i) tests do not respect naming convention" % (warn_name_count, len(test_runner.tests))
        ui.info(ui.red, "*", ui.yellow, msg)
    if warn_type_count:
        msg = "(%i/%i) tests do not have any type" % (warn_type_count, len(test_runner.tests))
        ui.info(ui.red, "*", ui.yellow, msg)
