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
        self.args = self.parser.parse_args([])
        if os.environ.get("DEBUG"):
            self.args.verbose = True
        if os.environ.get("PDB"):
            self.args.pdb = True
        self.args.work_tree = self.test_dir

    def test_configure_world(self):
        qitools.run_action("qibuild.actions.configure", ["world"],
            forward_args=self.args)

    def test_make_hello(self):
        qitools.run_action("qibuild.actions.configure", ["hello"],
            forward_args=self.args)
        qitools.run_action("qibuild.actions.make", ["hello"],
            forward_args=self.args)

    def test_install_hello(self):
        qitools.run_action("qibuild.actions.configure", ["hello"],
            forward_args=self.args)
        qitools.run_action("qibuild.actions.make", ["hello"],
            forward_args=self.args)
        qitools.run_action("qibuild.actions.install", ["hello", "/tmp"],
            forward_args=self.args)

    def test_ctest_hello(self):
        qitools.run_action("qibuild.actions.configure", ["hello"],
            forward_args=self.args)
        qitools.run_action("qibuild.actions.make", ["hello"],
            forward_args=self.args)
        qitools.run_action("qibuild.actions.test", ["hello"],
            forward_args=self.args)

    def tearDown(self):
        # TODO: remove build dirs
        pass


if __name__ == "__main__":
    unittest.main()
