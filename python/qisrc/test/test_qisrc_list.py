# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.


def test_simple(qisrc_action, record_messages):
    qisrc_action.git_worktree.create_git_project("world")
    qisrc_action("list")
    assert record_messages.find("world")


def test_empty(qisrc_action, record_messages):
    qisrc_action("list")
    assert record_messages.find("Tips")


def test_with_pattern(qisrc_action, record_messages):
    qisrc_action.git_worktree.create_git_project("world")
    qisrc_action.git_worktree.create_git_project("hello")
    record_messages.reset()
    qisrc_action("list", "worl.?")
    assert record_messages.find("world")
    assert not record_messages.find("hello")


def test_with_groups(qisrc_action, git_server, record_messages):
    git_server.create_group("foo", ["a.git"])
    git_server.create_group("bar", ["b.git"])
    qisrc_action("init", git_server.manifest_url)
    record_messages.reset()
    qisrc_action("list", "--group", "foo")
    assert record_messages.find("a.git")
    assert not record_messages.find("b.git")
