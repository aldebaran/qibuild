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
        # Backup the .qi/build.cfg
        qi_cfg_path = os.path.join(self.test_dir, ".qi", "build.cfg")
        qi_cfg = ""
        with open(qi_cfg_path, "r") as fp:
            qi_cfg = fp.read()
        # Run git clean -fdx to be sure build dir is clean:
        qitools.command.check_call(["git", "clean", "-fdx"],
                cwd=self.test_dir,
                ignore_ret_code = True)
        # Re-write the .qi/build.cfg file:
        qitools.sh.mkdir(os.path.join(self.test_dir, ".qi"))
        with open(qi_cfg_path, "w") as fp:
            fp.write(qi_cfg)


    def _run_action(self, action, *args):
        qitools.run_action("qibuild.actions.%s" % action, args,
            forward_args=self.args)

    def test_configure(self):
        self._run_action("configure", "world")

    def test_make(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")

    def test_make_without_configure(self):
        self.assertRaises(SystemExit, self._run_action, "make", "hello")

    def test_install(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")
        self._run_action("install", "hello", "/tmp")

    def test_ctest(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")
        self._run_action("test", "hello")

    def test_bdist(self):
        self._run_action("bdist", "world")


if __name__ == "__main__":
    unittest.main()
