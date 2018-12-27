#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Remove """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qisys.test.conftest import TestWorkTree


def test_qisrc_remove_existing(qisrc_action):
    """ Test QiSrc Remove Existing """
    worktree = qisrc_action.worktree
    worktree.create_project("foo")
    qisrc_action("remove", "foo")
    worktree = TestWorkTree()
    assert not worktree.get_project("foo")
    assert worktree.tmpdir.join("foo").check(dir=True)


def test_qisrc_remove_existing_from_disk(qisrc_action):
    """ Test QiSrc Remove Existing From Disk """
    worktree = qisrc_action.worktree
    worktree.create_project("foo")
    qisrc_action("remove", "foo", "--from-disk")
    worktree = TestWorkTree()
    assert not worktree.get_project("foo")
    assert not worktree.tmpdir.join("foo").check(dir=True)


def test_qisrc_fails_when_not_exists(qisrc_action):
    """ Test QiSrc Fails When Not Exists """
    error = qisrc_action("remove", "foo", raises=True)
    assert "No project in 'foo'" in error
