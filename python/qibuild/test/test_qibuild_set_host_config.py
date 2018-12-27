#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Set Host Config """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

import qibuild.config


def test_set_host_config_happy_path(qibuild_action):
    """ Test Set Host Config Happy """
    qibuild.config.add_build_config("foo")
    qibuild_action("set-host-config", "foo")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    assert qibuild_cfg.get_host_config() == "foo"


def test_set_host_config_no_such_config(qibuild_action):
    """ Test Set Host Config No Such Config """
    with pytest.raises(Exception) as e:
        qibuild_action("set-host-config", "foo")
    assert "No such config" in e.value.message
