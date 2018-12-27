#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiToolchain Package Info """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qibuild.test.conftest import record_messages
from qitoolchain.test.conftest import qitoolchain_action, toolchains


def test_simple(qitoolchain_action, toolchains, record_messages):
    """ Test Simple """
    toolchains.create("foo")
    toolchains.add_package("foo", "boost", package_version="1.57-r3")
    qitoolchain_action("package-info", "--toolchain", "foo", "boost")
    assert record_messages.find("boost 1.57-r3")
