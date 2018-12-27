#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiToolchain Create """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qitoolchain.qipackage
from qisrc.test.conftest import git_server


def test_simple(qitoolchain_action):
    """ Test Simple """
    assert qitoolchain_action("create", "foo").packages == list()


def test_git_feed(qitoolchain_action, git_server, feed):
    """ Test Git Feed """
    boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.44")
    feed.add_package(boost_package)
    git_server.create_repo("toolchains.git")
    git_server.change_branch("toolchains.git", "devel")
    git_server.push_file("toolchains.git", "feeds/foo.xml", feed.feed_xml.read(), branch="devel")
    feed_url = git_server.get_repo("toolchains.git").clone_url
    qitoolchain_action("create", "--feed-name", "foo", "--branch", "devel", "foo", feed_url)
    new_boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.55")
    feed.add_package(new_boost_package)
    git_server.push_file("toolchains.git", "feeds/foo.xml", feed.feed_xml.read(), branch="devel")
    qitoolchain_action("update", "foo")
    foo_tc = qitoolchain.get_toolchain("foo")
    assert foo_tc.get_package("boost").version == "1.55"
