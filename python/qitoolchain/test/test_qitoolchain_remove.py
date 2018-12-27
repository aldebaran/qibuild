#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiToolcahin Remove """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

import qitoolchain.toolchain
import qibuild.config
from qibuild.test.conftest import TestBuildWorkTree


def test_simple(qitoolchain_action):
    """ Test Simple """
    qitoolchain.toolchain.Toolchain("foo")
    qitoolchain_action("remove", "-f", "foo")
    with pytest.raises(Exception):
        qitoolchain.get_toolchain("foo")


def test_when_not_exists(qitoolchain_action):
    """ Test When Does not Exists """
    with pytest.raises(Exception) as e:
        qitoolchain_action("remove", "foo")
    assert "No such toolchain" in str(e.value)


def test_when_is_default(qitoolchain_action):
    """ Test When Is Default """
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    test_build_worktre1 = TestBuildWorkTree()
    test_build_worktre1.set_default_config("foo")
    qitoolchain_action("remove", "foo", "--force")
    test_build_worktre2 = TestBuildWorkTree()
    with pytest.raises(Exception) as e:
        test_build_worktre2.toolchain  # pylint:disable=pointless-statement
    assert "No such toolchain" in e.value.message
