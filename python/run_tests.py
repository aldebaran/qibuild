"""Use this script to run tests.

Make sure that this script is run with the correct
working dir, so that python libraries are found
"""

import os
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
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    qi_build_cfg = os.path.join(cur_dir,
        "qibuild", "test", "build-%s.cfg" % build_config)
    qi_test_dir = os.path.join(cur_dir,
        "qibuild", "test", ".qi")
    qitools.sh.mkdir(qi_test_dir, recursive=True)
    shutil.copy(qi_build_cfg, os.path.join(qi_test_dir, "build.cfg"))
    # If you do not use "-s" here, on windows, a bunch of cmd.exe
    # windows will be created, and nosetests will exit with error code
    # 1 without any error mesage...
    qitools.command.check_call(["nosetests", "-s", "qibuild"], shell=True)



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
    run_tests(xml_report=args.xml_report, build_config=args.build_config)

if __name__ == "__main__":
    main()




