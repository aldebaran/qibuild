#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Parsers """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

import qitoolchain.parsers
from qitoolchain.test.conftest import toolchains
import qibuild.config
from qibuild.test.conftest import build_worktree, args


def test_using_dash_c(toolchains, args):
    """ Test Using Dash C """
    foo_tc = toolchains.create("foo")
    qibuild.config.add_build_config("bar", toolchain="foo")
    qibuild.config.add_build_config("baz")
    args.config = "bar"
    assert qitoolchain.parsers.get_toolchain(args) == foo_tc
    args.config = "baz"
    with pytest.raises(Exception) as e:
        qitoolchain.parsers.get_toolchain(args)
    assert "config baz has no toolchain" in e.value.message


def test_using_defaut_config(toolchains, args, build_worktree):
    """ Test Using Default Config """
    qibuild.config.add_build_config("foo", toolchain="foo")
    foo_tc = toolchains.create("foo")
    build_worktree.set_default_config("foo")
    args.worktree = build_worktree.root
    assert qitoolchain.parsers.get_toolchain(args) == foo_tc
