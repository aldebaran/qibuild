""" List the tests"""


import os
import sys
from qisys import ui

import qisys.parsers
import qitest.conf
from qitest.runner import match_pattern

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    group = parser.add_argument_group("qitest list options")
    group.add_argument("qitest_json", help="path to a qitest.json file")
    group.add_argument("-k", "--pattern", dest="pattern",
                        help="Filter tests matching this pattern")

def do(args):
    qitest_json = args.qitest_json
    pattern = args.pattern
    tests = qitest.conf.parse_tests(qitest_json)
    matching_names = [x["name"] for x in tests if
                      match_pattern(pattern, x["name"])]
    for i, test_name in enumerate(matching_names):
        ui.info_count(i, len(matching_names), test_name)
