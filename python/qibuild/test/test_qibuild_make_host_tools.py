#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Make Host Tools """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.find


def test_make_host_tools(qibuild_action, fake_ctc):
    """ Test Make Host Tools """
    footool_proj = qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    qibuild_action("make-host-tools", "usefootool")
    qibuild.find.find_bin([footool_proj.sdk_directory], "footool", expect_one=True)
    qibuild_action("configure", "usefootool", "--config", "fake-ctc")


def test_recurse_deps(qibuild_action):
    """ Test Recurse Deps """
    footool_proj = qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    qibuild_action.create_project("bar", run_depends=["usefootool"])
    qibuild_action("make-host-tools", "bar")
    qibuild.find.find_bin([footool_proj.sdk_directory], "footool", expect_one=True)


def test_building_host_tools_in_release(qibuild_action, record_messages):
    """ Test Building Host Tools In Release """
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    record_messages.reset()
    qibuild_action("make-host-tools", "--release", "usefootool")
    assert record_messages.find("Building footool in Release")
    qibuild_action("configure", "usefootool")
    qibuild_action("make", "usefootool")


def test_no_project_specified(qibuild_action):
    """ Test No Project Specified """
    qibuild_action.add_test_project("footool")
    usefootool_proj = qibuild_action.add_test_project("usefootool")
    qibuild_action.chdir(usefootool_proj.path)
    qibuild_action("make-host-tools")
    qibuild_action("configure")


def test_using_dash_all(qibuild_action):
    """ Test Using Dash All """
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    qibuild_action("make-host-tools", "--all")
    qibuild_action("configure", "usefootool")
