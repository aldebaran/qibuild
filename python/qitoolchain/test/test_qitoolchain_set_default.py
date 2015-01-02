## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qibuild.test.conftest import TestBuildWorkTree

def test_simple(qitoolchain_action):
    qitoolchain_action("create", "foo")
    qitoolchain_action("set-default", "-c", "foo")
    build_worktree = TestBuildWorkTree()
    toolchain = build_worktree.toolchain
    assert toolchain
    assert toolchain.name == "foo"
