## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qisrc.test.conftest import TestGitWorkTree

def test_qisrc_add_dot(qisrc_action):
    tmpdir = qisrc_action.tmpdir
    foo = tmpdir.mkdir("foo")
    qisrc_action("add", ".", cwd=foo)
    # qisrc_action re-creates a worktree, so we have
    # to reload it to get the changes
    qisrc_action.reload_worktree()
    worktree = qisrc_action.worktree
    assert worktree.get_project("foo")

def test_qisrc_add_url_at_root(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    qisrc_action("add", foo.clone_url)
    git_worktree = TestGitWorkTree()
    assert git_worktree.get_git_project("foo")

def test_qisrc_add_url_in_subdir(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    lib = qisrc_action.tmpdir.mkdir("lib")
    qisrc_action("add", foo.clone_url, cwd=lib)
    qisrc_action.reload_worktree()
    git_worktree = qisrc_action.git_worktree
    assert git_worktree.get_git_project("lib/foo")

def test_qisrc_add_already_exists(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    qisrc_action.tmpdir.mkdir("foo")
    error = qisrc_action("add", foo.clone_url, raises=True)
    assert "already exists" in error
