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

import qibuild

def run_tests():
    """Prepare the test/ subdir, run nosetests with correct
    options

    """
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, cur_dir)
    qi_test_dir = os.path.join(cur_dir, "qibuild", "test", ".qi")
    qibuild.sh.mkdir(qi_test_dir, recursive=True)
    with open(os.path.join(qi_test_dir, "qibuild.xml"), "w") as fp:
        fp.write("<qibuild />")
    nose.main()

if __name__ == "__main__":
    run_tests()
