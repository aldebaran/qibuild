## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Collection of parser fonctions for qitests actions
"""

import qisys.parsers

def test_parser(parser, with_num_jobs=True):
    group = parser.add_argument_group("test options")
    group.add_argument("--perf", dest="perf", action="store_true",
                        help="run perfs tests instead of pure tests.")
    group.add_argument("-k", "--pattern", dest="pattern",
                        help="Filter tests matching this pattern")
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
    if with_num_jobs:
        group.add_argument("-j", dest="num_jobs", default=1, type=int,
                            help="Number of tests to run in parallel")
