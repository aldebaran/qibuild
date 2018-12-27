#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Info """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qisrc.test.conftest import git_server, qisrc_action


def test_info(qibuild_action, qisrc_action, git_server, record_messages):
    """ Test Info """
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    foo_project = qibuild_action.create_project("foo")
    record_messages.reset()
    qibuild_action("info", "foo")
    assert record_messages.find("src: foo")
    assert record_messages.find("repo: foo.git")
    qibuild_action.chdir(foo_project.path)
    record_messages.reset()
    qibuild_action("info")
    assert record_messages.find("Build project: foo")
