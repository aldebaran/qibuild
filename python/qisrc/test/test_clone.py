## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import unittest
import tempfile

import pytest

import qisrc
import qisrc.sync
import qibuild
from qisrc.test.test_git import create_git_repo


# pylint: disable-msg=E1101
@pytest.mark.slow
class CloneProjectTestCase(unittest.TestCase):
    def setUp(self):
        qibuild.command.CONFIG["quiet"] = True
        self.tmp = tempfile.mkdtemp(prefix="test-qisrc-sync")
        qibuild.sh.mkdir(self.tmp)
        self.srv = os.path.join(self.tmp, "srv")
        qibuild.sh.mkdir(self.srv)
        worktree_root = os.path.join(self.tmp, "work")
        qibuild.sh.mkdir(worktree_root)
        self.worktree = qisrc.worktree.open_worktree(worktree_root)

    def tearDown(self):
        qibuild.command.CONFIG["false"] = True
        qibuild.sh.rm(self.tmp)

    def test_simple_clone(self):
        bar_url = create_git_repo(self.tmp, "bar")
        qisrc.sync.clone_project(self.worktree, bar_url)
        self.assertEqual(self.worktree.git_projects[0].src, "bar")

    def test_clone_skipping(self):
        bar_url = create_git_repo(self.tmp, "bar")
        qisrc.sync.clone_project(self.worktree, bar_url)
        self.assertEqual(self.worktree.git_projects[0].src, "bar")
        qisrc.sync.clone_project(self.worktree, bar_url, skip_if_exists=True)
        self.assertEqual(len(self.worktree.git_projects), 1)
        self.assertEqual(self.worktree.git_projects[0].src, "bar")

    def test_clone_project_already_exists(self):
        bar_url = create_git_repo(self.tmp, "bar")
        baz_url = create_git_repo(self.tmp, "baz")
        qisrc.sync.clone_project(self.worktree, bar_url, src="bar")
        error = None
        try:
            qisrc.sync.clone_project(self.worktree, baz_url, src="bar")
        except Exception, e:
            error = e
        self.assertFalse(error is None)
        self.assertTrue("already registered" in str(error))

    def test_clone_path_already_exists(self):
        bar_url = create_git_repo(self.tmp, "bar")
        conflicting_path = os.path.join(self.worktree.root, "bar")
        qibuild.sh.mkdir(conflicting_path)
        error = None
        try:
            qisrc.sync.clone_project(self.worktree, bar_url)
        except Exception, e:
            error = e

        self.assertFalse(error is None)
        self.assertTrue("already exists" in str(error), error)
        qisrc.sync.clone_project(self.worktree, bar_url, src="baz")
        self.assertEqual(self.worktree.git_projects[0].src, "baz")

if __name__ == "__main__":
    unittest.main()
