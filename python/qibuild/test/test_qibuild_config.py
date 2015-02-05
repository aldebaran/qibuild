## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest

import qibuild.config

def test_show(qibuild_action):
    # Just check it does not crash for now
    qibuild_action("config", "show")

def test_run_wizard(qibuild_action, interact):
    interact.answers = {
        "generator" : "Unix Makefiles",
        "ide" : "None",
    }

    qibuild_action("config", "wizard")

def test_add_config(qibuild_action):
    qibuild_action("config", "add", "foo",
                   "--toolchain", "foo",
                   "--profile", "bar", "--profile", "baz",
                   "--cmake-generator", "ninja",
                   "--ide", "QtCreator")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    foo_cfg = qibuild_cfg.configs.get("foo")
    assert foo_cfg.name == "foo"

def test_set_default_config(qibuild_action, build_worktree):
    qibuild_action("config", "add", "foo", "--default")
    assert build_worktree.default_config == "foo"

def test_remove(qibuild_action):
    qibuild_action("config", "add", "foo", "--toolchain", "foo")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    assert qibuild_cfg.configs.get("foo")
    qibuild_action("config", "remove", "foo")
    qibuild_cfg2 = qibuild.config.QiBuildConfig()
    qibuild_cfg2.read()
    assert qibuild_cfg2.configs.get("foo") is None
