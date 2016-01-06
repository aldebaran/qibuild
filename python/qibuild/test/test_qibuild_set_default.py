## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qibuild.config
from qibuild.test.conftest import TestBuildWorkTree

def test_simple(qibuild_action):
    qibuild.config.add_build_config("foo")
    qibuild_action("set-default", "foo")
    build_worktree = TestBuildWorkTree()
    assert build_worktree.build_config.active_build_config.name == "foo"
