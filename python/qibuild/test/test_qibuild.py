"""Automatic testing for qibuild

"""

# Those are high-level tests, using sources from
# qibuild/python/qibuild/tests

import os
import sys
import unittest
import qitools
import qibuild

try:
    import argparse
except ImportError:
    from qitools.external import argparse


class QiBuildTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath(os.path.dirname(__file__))
        self.parser = argparse.ArgumentParser()
        qibuild.parsers.toc_parser(self.parser)
        qibuild.parsers.build_parser(self.parser)

    def test_configure_hello(self):
        args = self.parser.parse_args(sys.argv[1:])
        if os.environ.get("DEBUG"):
            args.verbose = True
        if os.environ.get("PDB"):
            args.pdb = True
        args.work_tree = self.test_dir
        qitools.run_action("qibuild.actions.configure",
            ["world"], forward_args=args)

    def tearDown(self):
        # TODO: remove build dirs
        pass


if __name__ == "__main__":
    unittest.main()
