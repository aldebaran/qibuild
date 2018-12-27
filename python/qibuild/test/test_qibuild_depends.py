#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Depends """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_simple(qibuild_action, record_messages):
    """ Test Simple """
    # More complex tests should be written at a lower level
    qibuild_action.create_project("world")
    qibuild_action.create_project("hello", build_depends=["world"])
    qibuild_action("depends", "hello")
