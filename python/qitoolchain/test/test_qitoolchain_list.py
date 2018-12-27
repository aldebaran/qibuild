#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QuToolchain List """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qibuild.test.conftest import record_messages
from qitoolchain.test.conftest import qitoolchain_action


def test_no_toolchain(qitoolchain_action, record_messages):
    """ Test No Toolchain """
    qitoolchain_action("list")
    assert record_messages.find("No toolchain yet")


def test_list(qitoolchain_action, record_messages):
    """ Test List """
    qitoolchain_action("create", "foo")
    qitoolchain_action("list")
    assert record_messages.find(r"\* foo")
