#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild List Profiles """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.profile
from qibuild.test.conftest import TestBuildWorkTree
from qisrc.test.conftest import qisrc_action, git_server


def test_list_profiles(qibuild_action, qisrc_action, git_server, record_messages):
    """ Test List Profiles """
    git_server.add_build_profile("foo", [("WITH_FOO", "ON")])
    qisrc_action("init", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    qibuild_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(qibuild_xml, "bar", [("WITH_BAR", "ON")])
    record_messages.reset()
    qibuild_action("list-profiles")
    assert record_messages.find(r"\*\s+foo")
    assert record_messages.find(r"\*\s+bar")
