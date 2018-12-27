#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Add Config """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.config


def test_add_config(qibuild_action):
    """ Test Add Config """
    qibuild_action("add-config", "foo",
                   "--toolchain", "foo",
                   "--profile", "bar", "--profile", "baz",
                   "--cmake-generator", "Ninja",
                   "--ide", "QtCreator")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    foo_cfg = qibuild_cfg.configs.get("foo")
    assert foo_cfg.name == "foo"
    assert foo_cfg.toolchain == "foo"
    assert foo_cfg.cmake.generator == "Ninja"
    assert foo_cfg.profiles == ["bar", "baz"]
    assert foo_cfg.ide == "QtCreator"


def test_set_default_config(qibuild_action, build_worktree):
    """ Test Set Default Config """
    qibuild_action("add-config", "foo", "--default")
    assert build_worktree.default_config == "foo"


def test_set_host_config(qibuild_action):
    """ Test Set Host Config """
    qibuild_action("add-config", "foo", "--host")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    assert qibuild_cfg.get_host_config() == "foo"


def test_re_adding_build_config_preserves_env(qibuild_action):
    """ Test Re Adding Build Config Preservces Env """
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    foo_config = qibuild.config.BuildConfig()
    foo_config.name = "foo"
    foo_config.env.path = "/path/to/foo/bin"
    qibuild_cfg.add_config(foo_config)
    qibuild_cfg.write()
    qibuild_action("add-config", "foo", "--toolchain", "foo")
    qibuild_cfg2 = qibuild.config.QiBuildConfig()
    qibuild_cfg2.read()
    foo_config = qibuild_cfg2.configs["foo"]
    assert foo_config.env.path == "/path/to/foo/bin"
