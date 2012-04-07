## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import unittest

import tempfile

import qisrc
import qibuild
from qisrc.test.test_sync import create_git_repo



class CloneProjectTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-qisrc-sync")
        qibuild.sh.mkdir(self.tmp)
        self.srv = os.path.join(self.tmp, "srv")
        qibuild.sh.mkdir(self.srv)
        worktree_root = os.path.join(self.tmp, "work")
        qibuild.sh.mkdir(worktree_root)
        self.worktree = qibuild.worktree.open_worktree(worktree_root)

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_simple_clone(self):
        bar_url = create_git_repo(self.tmp, "bar")
        qisrc.sync.clone_project(self.worktree, bar_url)
        self.assertEqual(self.worktree.git_projects[0].name, "bar")

    def test_clone_skipping(self):
        bar_url = create_git_repo(self.tmp, "bar")
        qisrc.sync.clone_project(self.worktree, bar_url)
        self.assertEqual(self.worktree.git_projects[0].name, "bar")
        qisrc.sync.clone_project(self.worktree, bar_url, skip_if_exists=True)
        self.assertEqual(len(self.worktree.git_projects), 1)
        self.assertEqual(self.worktree.git_projects[0].name, "bar")

    def test_clone_already_project_already_exists(self):
        bar_url = create_git_repo(self.tmp, "bar")
        baz_url = create_git_repo(self.tmp, "baz")
        qisrc.sync.clone_project(self.worktree, bar_url, name="bar")
        error = None
        try:
            qisrc.sync.clone_project(self.worktree, baz_url, name="bar")
        except Exception, e:
            error = e
        self.assertFalse(error is None)
        self.assertTrue("A project named bar already exists" in str(error))

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
        self.assertTrue("Path %s already exists" % conflicting_path in str(error))
        qisrc.sync.clone_project(self.worktree, bar_url, name="bar", path="baz")
        self.assertEqual(self.worktree.git_projects[0].name, "bar")
        self.assertEqual(self.worktree.git_projects[0].src,
            os.path.join(self.worktree.root, "baz"))
