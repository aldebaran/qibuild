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

def do(args):
    test_runner = qitest.parsers.get_test_runner(args)
    for i, test in enumerate(test_runner.tests):
        ui.info_count(i, len(test_runner.tests), test["name"])
