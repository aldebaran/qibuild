#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_simple(qipy_action, record_messages):
    """ Test Simple """
    qipy_action.add_test_project("a_lib")
    qipy_action.add_test_project("big_project")
    qipy_action.add_test_project("foomodules")
    qipy_action("list")
    assert record_messages.find(r"\*\s+a")
    assert record_messages.find(r"\*\s+big_project")
