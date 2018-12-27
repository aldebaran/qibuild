#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_simple(git_server, qisrc_action, record_messages):
    """ Test Simple """
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_server.push_file("foo.git", "devel",
                         "this is devel\n", branch="devel",
                         message="start developing")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    record_messages.reset()
    qisrc_action("diff", "--all", "master")
    assert record_messages.find("devel | 1 +")
