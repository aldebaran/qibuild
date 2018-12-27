#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Rm Group """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qisrc.test.conftest import TestGitWorkTree


def test_qisrc_rm_group(qisrc_action, git_server):
    """ Test QiSrc Rm Group """
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
    """ Test Switchin Group """
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
    """ Test QiSrc Remove Default Group """
    git_server.create_group("default", ["a", "b"], default=True)
    git_server.create_group("minimal", ["a"])
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2
    qisrc_action("rm-group", "default")
    git_worktree = TestGitWorkTree()
    assert not git_worktree.git_projects
    qisrc_action("add-group", "minimal")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1
