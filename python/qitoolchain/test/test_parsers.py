## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qitoolchain.parsers
from qibuild.test.conftest import build_worktree

def test_using_dash_c(toolchains, args):
    foo_tc = toolchains.create("foo")
    args.config = "foo"
    assert qitoolchain.parsers.get_toolchain(args) == foo_tc

def test_using_defaut_config(toolchains, args, build_worktree):
    foo_tc = toolchains.create("foo")
    build_worktree.set_default_config("foo")
    args.worktree = build_worktree.root
    assert qitoolchain.parsers.get_toolchain(args) == foo_tc

