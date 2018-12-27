#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Status """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_simple(qibuild_action, record_messages):
    """ Test Simple """
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "world")
    record_messages.reset()
    qibuild_action("status")
    assert record_messages.find("world")
    assert record_messages.find("hello")
