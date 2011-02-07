#!/usr/bin/env python
"""Use this script to run tests.

Make sure that this script is run with the correct
working dir, so that python libraries are found
"""

import os
import sys
import shutil
import qitools
try:
    import argparse
except ImportError:
    from qitools.external import argparse

BUILD_CONFIGS = ["unix", "vs2008"]

def run_tests(xml_report=False, build_config="unix"):
    """Prepare the test/ subdir, run nosetests with correct
    options

    """
    import unittest
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    qi_build_cfg = os.path.join(cur_dir,
        "qibuild", "test", "build-%s.cfg" % build_config)
    qi_test_dir = os.path.join(cur_dir,
        "qibuild", "test", ".qi")
    qitools.sh.mkdir(qi_test_dir, recursive=True)
    shutil.copy(qi_build_cfg, os.path.join(qi_test_dir, "build.cfg"))

    from qibuild.test.test_qibuild import QiBuildTestCase
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(QiBuildTestCase))
    out_xml = qitools.sh.to_native_path(os.path.join(cur_dir, "..", "tests-results.xml"))

    if xml_report:
        from xmlrunner import XmlTestRunner
        with open(out_xml, "w") as fp:
            runner = XmlTestRunner(fp)
            runner.run(suite)

    else:
        unittest.TextTestRunner().run(suite)


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




