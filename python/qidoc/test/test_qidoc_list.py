#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_simple(qidoc_action, record_messages):
    """ Test Simple """
    qidoc_action.add_test_project("world")
    qidoc_action.add_test_project("libworld")
    qidoc_action("list")
    assert record_messages.find(r"\*\s+world")
    assert record_messages.find(r"\*\s+libworld")
