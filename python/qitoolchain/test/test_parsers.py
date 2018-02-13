# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import pytest

import qibuild.config
from qibuild.test.conftest import build_worktree  # pylint: disable=unused-import

import qitoolchain.parsers

# pylint: disable=redefined-outer-name


def test_using_dash_c(toolchains, args):
    foo_tc = toolchains.create("foo")
    qibuild.config.add_build_config("bar", toolchain="foo")
    qibuild.config.add_build_config("baz")
    args.config = "bar"
    assert qitoolchain.parsers.get_toolchain(args) == foo_tc
    args.config = "baz"
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qitoolchain.parsers.get_toolchain(args)
    assert "config baz has no toolchain" in e.value.message


def test_using_defaut_config(toolchains, args, build_worktree):
    qibuild.config.add_build_config("foo", toolchain="foo")
    foo_tc = toolchains.create("foo")
    build_worktree.set_default_config("foo")
    args.worktree = build_worktree.root
    assert qitoolchain.parsers.get_toolchain(args) == foo_tc
