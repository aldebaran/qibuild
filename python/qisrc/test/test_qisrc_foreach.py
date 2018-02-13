# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.


def test_qisrc_foreach(qisrc_action, record_messages):
    worktree = qisrc_action.worktree
    worktree.create_project("not_in_git")
    git_worktree = qisrc_action.git_worktree
    git_worktree.create_git_project("git_project")
    qisrc_action("foreach", "ls")
    assert not record_messages.find("not_in_git")
    assert record_messages.find("git_project")
    record_messages.reset()
    qisrc_action("foreach", "ls", "--all")
    assert record_messages.find("not_in_git")
    assert record_messages.find("git_project")


def test_non_cloned_groups(qisrc_action, git_server, record_messages):
    git_server.create_group("foo", ["a.git", "b.git"])
    git_server.create_group("bar", ["b.git", "c.git"])
    qisrc_action("init", git_server.manifest_url, "--group", "foo")
    record_messages.reset()
    qisrc_action("foreach", "--group", "bar", "ls")
    warning = record_messages.find(r"\[WARN \]")
    assert warning
    assert "Group bar is not currently in use" in warning


def test_do_not_warn_on_subgroups(qisrc_action, git_server, record_messages):
    git_server.create_group("big", ["a.git", "b.git"])
    git_server.create_group("small", ["b.git"])
    qisrc_action("init", git_server.manifest_url, "--group", "big")
    record_messages.reset()
    qisrc_action("foreach", "--group", "small", "ls")
    assert not record_messages.find(r"\[WARN \]")
    assert record_messages.find(r"\* \(1/1\) b")
