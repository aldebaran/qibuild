#!/usr/bin/env python
## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Use this script to run tests.

Make sure that this script is run with the correct
working dir, so that python libraries are found
"""

import os
import sys
import nose
import argparse

import qibuild

def run_tests(args):
    """Prepare the test/ subdir, run nosetests with correct
    options

    """
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, cur_dir)
    qi_test_dir = os.path.join(cur_dir, "qibuild", "test", ".qi")
    qibuild.sh.mkdir(qi_test_dir, recursive=True)
    with open(os.path.join(qi_test_dir, "qibuild.xml"), "w") as fp:
        fp.write("<qibuild />")
    nose_args = ["nose"]
    if args.coverage:
        nose_args.append("--with-coverage")
    if args.xunit:
        nose_args.append("--with-xunit")
    nose.main(argv=nose_args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", action="store_true")
    parser.add_argument("--xunit", action="store_true")
    args = parser.parse_args()
    run_tests(args)
