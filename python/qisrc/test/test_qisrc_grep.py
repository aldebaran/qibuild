#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Grep """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import py

import qisrc.git


def setup_projects(qisrc_action):
    """ Create two git projects with one match for the "spam" pattern """
    foo_proj = qisrc_action.create_git_project("foo")
    bar_proj = qisrc_action.create_git_project("bar")
    foo_path = py.path.local(foo_proj.path)  # pylint:disable=no-member
    foo_git = qisrc.git.Git(foo_proj.path)
    _bar_git = qisrc.git.Git(bar_proj.path)
    foo_path.join("a.txt").write("this is spam\n")
    foo_git.add("a.txt")


def test_all_by_default(qisrc_action, record_messages):
    """ Test All By Default """
    setup_projects(qisrc_action)
    record_messages.reset()
    rc = qisrc_action("grep", "spam", retcode=True)
    assert rc == 0
    assert record_messages.find("foo")
    assert record_messages.find("bar")
    assert record_messages.find("this is spam")


def test_using_projects(qisrc_action):
    """ Test Using Projects """
    setup_projects(qisrc_action)
    rc = qisrc_action("grep", "-p", "foo", "spam", retcode=True)
    assert rc == 0
    rc = qisrc_action("grep", "-p", "bar", "spam", retcode=True)
    assert rc == 1


def test_using_git_grep_options(qisrc_action, record_messages):
    """ Test Usin Git Grep Option """
    setup_projects(qisrc_action)
    rc = qisrc_action("grep", "--", "-i", "-l", "Spam", retcode=True)
    assert rc == 0
    assert record_messages.find("a.txt")


def test_worktree_paths(qisrc_action, record_messages):
    """ Test Wortree Paths """
    setup_projects(qisrc_action)
    _rc = qisrc_action("grep", "--path", "worktree", "--", "-i", "-l", "Spam", retcode=True)
    assert record_messages.find("foo/a.txt")
