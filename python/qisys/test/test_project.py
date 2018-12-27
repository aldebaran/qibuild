#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Project """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qisys.test.conftest import TestWorkTree


def test_get_set_license(worktree):
    """ Test Get Set Licence """
    food = worktree.create_project("foo")
    assert food.license is None
    food.license = "GPL"
    assert food.license == "GPL"
    worktree2 = TestWorkTree()
    foo2 = worktree2.get_project("foo")
    assert foo2.license == "GPL"
