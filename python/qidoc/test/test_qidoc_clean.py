#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os


def test_simple(qidoc_action):
    """ Test Simple """
    world_proj = qidoc_action.add_test_project("world")
    build_dir = os.path.join(world_proj.path, "build-doc")
    assert not os.path.exists(build_dir)
    qidoc_action("build", "world")
    assert os.path.exists(build_dir)
    qidoc_action("clean", "world")
    assert os.path.exists(build_dir)
    qidoc_action("clean", "world", "--force")
    assert not os.path.exists(build_dir)
