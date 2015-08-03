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
import qitest.parsers
import qibuild.parsers

def configure_parser(parser):
    qitest.parsers.test_parser(parser)
    qibuild.parsers.project_parser(parser)
    qisys.parsers.build_parser(parser, include_worktree_parser=False)

def do(args):
    test_runners = qitest.parsers.get_test_runners(args)

    # rule to check for tests which doesn't follow naming convention
    expr = re.compile("^test_.*")
    warn_name_count = 0
    warn_type_count = 0
    for test_runner in test_runners:
        ui.info("Tests in ", test_runner.project.sdk_directory)
        for i, test in enumerate(test_runner.tests):
            n = len(test_runner.tests)
            name = test["name"]
            name_ok = re.match(expr, name)
            type_ok = (test.get("pytest") or test.get("gtest"))
            if name_ok and type_ok:
                ui.info_count(i, n, test["name"])
            else:
                message = ""
                if not name_ok:
                    warn_name_count += 1
                    message += "(invalid name) "
                if not type_ok:
                    warn_type_count += 1
                    message += "(no type)"
                ui.info_count(i, n, name, ui.brown, message)

    if warn_name_count:
        msg = "%i on %i tests do not respect naming convention" % (warn_name_count, len(test_runner.tests))
        ui.warning(msg)
    if warn_type_count:
        msg = "%i on %i tests do not have any type" % (warn_type_count, len(test_runner.tests))
        ui.warning(msg)
