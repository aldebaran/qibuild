#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiToolchain Remove Package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.config
import qitoolchain.toolchain


def test_simple(qitoolchain_action):
    """ Test Simple """
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    word_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo", word_package)
    qitoolchain_action("remove-package", "-c", "foo", "world")
    foop = qitoolchain.get_toolchain("foo")
    assert foop.packages == list()


def test_fails_when_no_such_package(qitoolchain_action):
    """ Test Fail When No Such Package """
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    error = qitoolchain_action("remove-package", "-c", "foo", "world", raises=True)
    assert "No such package" in error
