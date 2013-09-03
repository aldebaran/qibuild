""" List the tests"""


import os
import sys
from qisys import ui

import qisys.parsers
import qitest.conf

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    group = parser.add_argument_group("qitest list options")
    group.add_argument("qitest_json", help="path to a qitest.json file")

def do(args):
    qitest_json = args.qitest_json
    tests = qitest.conf.parse_tests(qitest_json)
    for i, test in enumerate(tests):
        ui.info_count(i, len(tests), test["name"])
