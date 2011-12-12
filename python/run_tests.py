#!/usr/bin/env python
## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Use this script to run tests.

Make sure that this script is run with the correct
working dir, so that python libraries are found
"""

import os
import sys
import shutil
import qibuild
try:
    import argparse
except ImportError:
    from qibuild.external import argparse

from qibuild.external.xmlrunner import XmlTestRunner

BUILD_CONFIGS = ["unix", "vs2008"]

from qibuild.test.test_qibuild import QiBuildTestCase
from qibuild.test.test_config  import QiConfigTestCase, TocCMakeFlagsTestCase
from qitoolchain.test.test_qitoolchain import QiToolchainTestCase, FeedTestCase

TEST_CASES = [
    QiBuildTestCase,
    QiConfigTestCase,
    TocCMakeFlagsTestCase,
    QiToolchainTestCase,
    FeedTestCase
]


def run_tests(xml_report=False, build_config="unix"):
    """Prepare the test/ subdir, run nosetests with correct
    options

    """
    import unittest
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    qi_test_dir = os.path.join(cur_dir, "qibuild", "test", ".qi")
    qibuild.sh.mkdir(qi_test_dir, recursive=True)

    suite = unittest.TestSuite()
    for test_case in TEST_CASES:
        suite.addTests(unittest.makeSuite(test_case))

    out_xml = qibuild.sh.to_native_path(os.path.join(cur_dir, "..", "tests-results.xml"))

    result = None
    if xml_report:
        with open(out_xml, "w") as fp:
            runner = XmlTestRunner(fp)
            result = runner.run(suite)
    else:
        runner = unittest.TextTestRunner()
        result = runner.run(suite)

    if not result.wasSuccessful():
        sys.exit(1)


def main():
    """Parse command line """
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml-report", action="store_true",
        help = "to be used on build farm: generate "
                "an XML report and store it in qibuild/build-test-results")
    parser.add_argument("--build-config", choices=BUILD_CONFIGS,
        help = "use a cutsom .qi/build.cfg for the tests")
    parser.set_defaults(
        xml_report=False,
        build_config="unix")

    args = parser.parse_args()

    # Quick small hack for hudson:
    build_config = args.build_config
    if not build_config:
        labels = os.environ.get("NODE_LABELS")
        if labels:
            if "vs2008" in labels:
                build_config = "vs2008"

    if sys.platform.startswith("win"):
        build_config = "vs2008"
    run_tests(xml_report=args.xml_report, build_config=build_config)

if __name__ == "__main__":
    main()




