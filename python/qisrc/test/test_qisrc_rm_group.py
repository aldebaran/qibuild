## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

from qisrc.test.conftest import TestGitWorkTree

def test_qisrc_rm_group(qisrc_action, git_server):
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_group("foobar", ["foo", "bar", "baz"])
    qisrc_action("init", git_server.manifest_url,
                "--group", "mygroup",
                "--group", "foobar")
    git_worktree = TestGitWorkTree()
    a_proj = git_worktree.get_git_project("a")
    b_proj = git_worktree.get_git_project("b")
    assert len(git_worktree.git_projects) == 5
    qisrc_action("rm-group", "foobar")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2
    # Better safe than sorry ...
    assert os.path.exists(a_proj.path)
    assert os.path.exists(b_proj.path)

def test_switching_group(qisrc_action, git_server):
    git_server.create_group("default",
                            ["naooqi", "agility", "vision", "choregraphe"],
                            default=True)
    git_server.create_group("agility", ["agility"])
    qisrc_action("init", git_server.manifest_url, "--group", "agility")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1
    qisrc_action("add-group", "default")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 4
    qisrc_action("rm-group", "default")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1

def test_qisrc_remove_default_group(qisrc_action, git_server):
    git_server.create_group("default", ["a", "b"], default=True)
    git_server.create_group("minimal", ["a"])
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2
    qisrc_action("rm-group", "default")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 0
    qisrc_action("add-group", "minimal")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1

def test_removing_group_from_disk(qisrc_action, git_server, interact):
    git_server.create_group("foo", ["a", "b"])
    git_server.create_group("bar", ["b", "c"])
    qisrc_action("init", git_server.manifest_url, "--group", "foo", "--group", "bar")
    d_url = git_server.create_repo("d").clone_url
    qisrc_action("add", d_url)
    git_worktree = TestGitWorkTree()
    a_path = git_worktree.get_git_project("a").path
    b_path = git_worktree.get_git_project("b").path
    c_path = git_worktree.get_git_project("c").path
    d_path = git_worktree.get_git_project("d").path

    interact.answers = [True]
    qisrc_action("rm-group", "foo", "--from-disk")
    # a should be removed
    # b should not be removed (still in 'bar' group)
    # d should not be removed (added manually)
    assert not os.path.exists(a_path)
    assert os.path.exists(b_path)
    assert os.path.exists(d_path)
