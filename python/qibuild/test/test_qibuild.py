## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for qibuild

"""


import os
import sys
import unittest
import qibuild
import qibuild

try:
    import argparse
except ImportError:
    from qibuild.external import argparse


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
        # Run qibuild clean
        self._run_action('clean', '-f')

    def _run_action(self, action, *args):
        qibuild.run_action("qibuild.actions.%s" % action, args,
            forward_args=self.args)

    def test_configure(self):
        self._run_action("configure", "world")

    def test_make(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")

    def test_make_without_configure(self):
        self.assertRaises(Exception, self._run_action, "make", "hello")

    def test_install(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")
        self._run_action("install", "hello", "/tmp")

    def test_ctest(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")
        self._run_action("test", "hello")

    def test_package(self):
        self._run_action("package", "world")


if __name__ == "__main__":
    unittest.main()
