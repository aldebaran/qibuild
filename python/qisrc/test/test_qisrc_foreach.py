#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Foreach """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_qisrc_foreach(qisrc_action, record_messages):
    """ Test QiSrc Foreach """
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
    """ Test Non Cloned Groups """
    git_server.create_group("foo", ["a.git", "b.git"])
    git_server.create_group("bar", ["b.git", "c.git"])
    qisrc_action("init", git_server.manifest_url, "--group", "foo")
    record_messages.reset()
    qisrc_action("foreach", "--group", "bar", "ls")
    warning = record_messages.find(r"\[WARN \]")
    assert warning
    assert "Group bar is not currently in use" in warning


def test_do_not_warn_on_subgroups(qisrc_action, git_server, record_messages):
    """ Test Do Not Warn On SubGroups """
    git_server.create_group("big", ["a.git", "b.git"])
    git_server.create_group("small", ["b.git"])
    qisrc_action("init", git_server.manifest_url, "--group", "big")
    record_messages.reset()
    qisrc_action("foreach", "--group", "small", "ls")
    assert not record_messages.find(r"\[WARN \]")
    assert record_messages.find(r"\* \(1/1\) b")
