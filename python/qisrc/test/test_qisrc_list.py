#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc List """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_simple(qisrc_action, record_messages):
    """ Test Simple """
    qisrc_action.git_worktree.create_git_project("world")
    qisrc_action("list")
    assert record_messages.find("world")


def test_empty(qisrc_action, record_messages):
    """ Test Empty """
    qisrc_action("list")
    assert record_messages.find("Tips")


def test_with_pattern(qisrc_action, record_messages):
    """ Test With Pattern """
    qisrc_action.git_worktree.create_git_project("world")
    qisrc_action.git_worktree.create_git_project("hello")
    record_messages.reset()
    qisrc_action("list", "worl.?")
    assert record_messages.find("world")
    assert not record_messages.find("hello")


def test_with_groups(qisrc_action, git_server, record_messages):
    """ Test With Groups """
    git_server.create_group("foo", ["a.git"])
    git_server.create_group("bar", ["b.git"])
    qisrc_action("init", git_server.manifest_url)
    record_messages.reset()
    qisrc_action("list", "--group", "foo")
    assert record_messages.find("a.git")
    assert not record_messages.find("b.git")
