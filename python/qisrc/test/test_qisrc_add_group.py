#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Add Group """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qisrc.test.conftest import TestGitWorkTree


def test_qisrc_add_group(qisrc_action, git_server):
    """ Test QiSrc Add Group """
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_group("foobar", ["foo", "bar", "baz"])
    qisrc_action("init", git_server.manifest_url, "--group", "mygroup")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2
    qisrc_action("add-group", "foobar")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 5


def test_add_group_after_using_default(qisrc_action, git_server):
    """ Test Add Group After Using Default """
    git_server.create_group("default", ["a"], default=True)
    git_server.create_group("mygroup", ["b", "c"])
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1
    qisrc_action("add-group", "mygroup")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3
