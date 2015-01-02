## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisrc.git
from qisrc.test.conftest import TestGitWorkTree

import py

def test_untracked(qisrc_action, record_messages):
    git_worktree = qisrc_action.git_worktree
    foo = git_worktree.create_git_project("foo")
    bar = git_worktree.create_git_project("bar")
    # pylint: disable-msg=E1101
    foo_path = py.path.local(foo.path)
    foo_path.ensure("untracked", file=True)
    qisrc_action("status")
    dirty = record_messages.find("Dirty projects")
    assert "0" in dirty

    record_messages.reset()
    qisrc_action("status", "-u")
    dirty = record_messages.find("Dirty projects")
    assert "1" in dirty

def test_behind(qisrc_action, git_server, record_messages):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo = git_worktree.get_git_project("foo")
    git_server.push_file("foo.git", "new_file", "")
    foo_git = qisrc.git.Git(foo.path)
    foo_git.fetch()
    qisrc_action("status")
    assert record_messages.find("foo : master tracking -1")

def test_wrong_branch(qisrc_action, git_server, record_messages):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo = git_worktree.get_git_project("foo")
    bar = git_worktree.get_git_project("bar")
    foo_git = qisrc.git.Git(foo.path)
    foo_git.checkout("-B", "devel")
    qisrc_action("status")
    assert record_messages.find("Some projects are not on the expected branch")
    assert record_messages.find(r"\* foo\s+devel\s+master")

def test_not_on_any_branch(qisrc_action, record_messages):
    git_worktree = TestGitWorkTree()
    foo = git_worktree.create_git_project("foo")
    foo_git = qisrc.git.Git(foo.path)
    (rc, out) = foo_git.call("log", "-1", "HEAD", "--pretty=%H", raises=False)
    foo_git.checkout(out)
    qisrc_action("status")
    assert record_messages.find("not on any branch")
