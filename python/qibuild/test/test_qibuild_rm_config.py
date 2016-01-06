## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qibuild.config
from qibuild.test.conftest import TestBuildWorkTree

def test_remove(qibuild_action):
    qibuild_action("add-config", "foo", "--toolchain", "foo")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    assert qibuild_cfg.configs.get("foo")
    qibuild_action("rm-config", "foo")
    qibuild_cfg2 = qibuild.config.QiBuildConfig()
    qibuild_cfg2.read()
    assert qibuild_cfg2.configs.get("foo") is None

def test_when_is_default(qibuild_action):
    qibuild_action("add-config", "foo", "--default")
    build_worktree = TestBuildWorkTree()
    assert build_worktree.build_config.active_build_config.name == "foo"
    qibuild_action("rm-config", "foo")
    build_worktree2 = TestBuildWorkTree()
    assert build_worktree2.build_config.active_build_config is None
