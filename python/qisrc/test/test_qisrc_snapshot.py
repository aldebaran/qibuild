#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Snapshot """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.snapshot


def test_simple(qisrc_action):
    """ Test Simple """
    qisrc_action.create_git_project("foo")
    qisrc_action.create_git_project("bar")
    res = qisrc_action("snapshot")
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.load(res)
    assert snapshot.format_version == 2


def test_with_argument(qisrc_action):
    """ Test With Argument """
    qisrc_action.create_git_project("foo")
    qisrc_action.create_git_project("bar")
    res = qisrc_action("snapshot", "blah.xml")
    assert res == "blah.xml"
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.load(res)
    assert snapshot.format_version == 2
