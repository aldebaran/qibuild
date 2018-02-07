# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
from qisrc.test.conftest import TestGitWorkTree


def test_qisrc_rm_group(qisrc_action, git_server):
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_group("foobar", ["foo", "bar", "baz"])
    qisrc_action("init", git_server.manifest_url,
                 "--group", "mygroup",
                 "--group", "foobar")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 5
    qisrc_action("rm-group", "foobar")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2


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
    assert len(git_worktree.git_projects) == 0  # pylint: disable=len-as-condition

    qisrc_action("add-group", "minimal")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1
