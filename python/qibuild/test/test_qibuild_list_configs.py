#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Tes QiBuild List Configs """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_list(qibuild_action, toolchains, record_messages):
    """ Test List """
    toolchains.create("foo")
    qibuild_action("add-config", "foo", "--toolchain", "foo")
    qibuild_action("add-config", "bar", "--profile", "bar")
    record_messages.reset()
    qibuild_action("list-configs")
    assert record_messages.find("foo\n  toolchain: foo")
    assert record_messages.find("bar\n  profiles: bar")
