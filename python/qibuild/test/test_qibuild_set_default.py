#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Set Default """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.config
from qibuild.test.conftest import TestBuildWorkTree


def test_simple(qibuild_action):
    """ Test Simple """
    qibuild.config.add_build_config("foo")
    qibuild_action("set-default", "foo")
    build_worktree = TestBuildWorkTree()
    assert build_worktree.build_config.active_build_config.name == "foo"
