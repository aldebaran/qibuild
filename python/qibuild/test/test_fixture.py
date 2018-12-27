#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Fixture """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_add_test_project(build_worktree):
    """ Test Add Test Project """
    _world = build_worktree.add_test_project("world")
    assert build_worktree.get_build_project("world")
