#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_list_groups(qisrc_action, git_server, record_messages):
    """ Test List Groups """
    git_server.create_group("default", ["foo", "bar"], default=True)
    git_server.create_group("spam", ["spam", "eggs"])
    qisrc_action("init", git_server.manifest_url)
    record_messages.reset()
    qisrc_action("list-groups")
    assert record_messages.find(r"\* default")
    assert record_messages.find(" spam")
