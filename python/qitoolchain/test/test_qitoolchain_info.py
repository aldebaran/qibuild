#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QuToolchain Info """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.config
from qibuild.test.conftest import record_messages
from qitoolchain.test.conftest import qitoolchain_action


def test_simple(qitoolchain_action, record_messages):
    """ Test Simple """
    qitoolchain_action("create", "foo")
    qitoolchain_action("create", "bar")
    qibuild.config.add_build_config("foo", toolchain="foo")
    world_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo", world_package)
    record_messages.reset()
    qitoolchain_action("info")
    assert record_messages.find("foo")
    assert record_messages.find("world")
    assert record_messages.find("bar")
    record_messages.reset()
    qitoolchain_action("info", "foo")
    assert record_messages.find("foo")
    assert record_messages.find("world")
    assert not record_messages.find("bar")
