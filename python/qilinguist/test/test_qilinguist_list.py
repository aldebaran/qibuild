#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qibuild.test.conftest import TestBuildWorkTree


def test_simple(qilinguist_action, record_messages):
    """ Test Simple """
    build_worktree = TestBuildWorkTree()
    build_worktree.add_test_project("translateme/qt")
    qilinguist_action("list")
    assert record_messages.find("\\*\\s+helloqt")
    assert record_messages.find("\\*\\s+translate")
