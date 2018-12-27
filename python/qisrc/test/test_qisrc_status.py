#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Status """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import py

import qisrc.git
from qisrc.test.conftest import TestGitWorkTree


def test_untracked(qisrc_action, record_messages):
    """ Test Untracked """
    git_worktree = qisrc_action.git_worktree
    foo1 = git_worktree.create_git_project("foo")
    _bar1 = git_worktree.create_git_project("bar")
    foo_path = py.path.local(foo1.path)  # pylint:disable=no-member
    foo_path.ensure("untracked", file=True)
    qisrc_action("status")
    dirty = record_messages.find("Dirty projects")
    assert "0" in dirty
    record_messages.reset()
    qisrc_action("status", "-u")
    dirty = record_messages.find("Dirty projects")
    assert "1" in dirty


def test_behind(qisrc_action, git_server, record_messages):
    """ Test Behind """
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo1 = git_worktree.get_git_project("foo")
    git_server.push_file("foo.git", "new_file", "")
    foo_git = qisrc.git.Git(foo1.path)
    foo_git.fetch()
    qisrc_action("status")
    assert record_messages.find("foo : master tracking -1")


def test_wrong_branch(qisrc_action, git_server, record_messages):
    """ Test Wrong Branch """
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo1 = git_worktree.get_git_project("foo")
    _bar1 = git_worktree.get_git_project("bar")
    foo_git = qisrc.git.Git(foo1.path)
    foo_git.checkout("-B", "devel")
    qisrc_action("status")
    assert record_messages.find("Some projects are not on the expected branch")
    assert record_messages.find(r"\* foo\s+devel\s+master")


def test_not_on_any_branch(qisrc_action, record_messages):
    """ Test Not On Any Branch """
    git_worktree = TestGitWorkTree()
    foo1 = git_worktree.create_git_project("foo")
    foo_git = qisrc.git.Git(foo1.path)
    (_rc, out) = foo_git.call("log", "-1", "HEAD", "--pretty=%H", raises=False)
    foo_git.checkout(out)
    qisrc_action("status")
    assert record_messages.find("not on any branch")


def test_fixed_ref_up_to_date(qisrc_action, git_server, record_messages):
    """ Test Fixed Ref Up To Date """
    git_server.create_repo("foo.git")
    git_server.push_tag("foo.git", "v0.1")
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("status")
    assert record_messages.find("foo fixed ref v0.1")
    record_messages.reset()
    qisrc_action("status", "--short")
    assert not record_messages.find("fixed ref")


def test_fixed_ref_behind(qisrc_action, git_server, record_messages):
    """ Test Fixed Ref Behind """
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    git.call("reset", "--hard", "HEAD~1")
    qisrc_action("status")
    assert record_messages.find("fixed ref v0.1 -1")
