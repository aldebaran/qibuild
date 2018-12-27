#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild List Binaries """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_list_binaries(qibuild_action, record_messages):
    """ Test List Binaries """
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    record_messages.reset()
    qibuild_action("list-binaries")
    assert record_messages.find("^ok$")
    assert record_messages.find("^fail$")
