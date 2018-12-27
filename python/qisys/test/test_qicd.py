#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiCd """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qicd


def get_best_match(worktree, token):
    """ Get Best Match """
    # qicd.find_best_match returns an absolute path,
    # this is used to simplify assertions
    res = qicd.find_best_match(worktree, token)
    if res:
        return os.path.relpath(res, worktree.root)
    return None


def test_matches_closest(worktree):
    """ Test Matches Closest """
    worktree.create_project("agility/motion")
    worktree.create_project("apps/behaviors")
    worktree.create_project("apps/core")
    worktree.create_project("behavior")
    worktree.create_project("chuck")
    worktree.create_project("core/naoqicore")
    worktree.create_project("gui/choregraphe")
    worktree.create_project("lib/libalmath")
    worktree.create_project("lib/libalmathinternal")
    worktree.create_project("navigation")
    worktree.create_project("sdk/libnaoqi")
    worktree.create_project("tools/java")
    assert get_best_match(worktree, "behaviors") == "apps/behaviors"
    assert get_best_match(worktree, "naoqic") == "core/naoqicore"
    assert get_best_match(worktree, "libnao") == "sdk/libnaoqi"
    assert get_best_match(worktree, "chor") == "gui/choregraphe"
    assert get_best_match(worktree, "nav") == "navigation"
    assert get_best_match(worktree, "mathint") == "lib/libalmathinternal"
    assert get_best_match(worktree, "almathin") == "lib/libalmathinternal"
    assert get_best_match(worktree, "almath") == "lib/libalmath"
