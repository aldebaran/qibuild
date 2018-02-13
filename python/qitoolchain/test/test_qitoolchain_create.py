# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

from qisrc.test.conftest import git_server  # pylint: disable=unused-import

import qitoolchain.qipackage

# pylint: disable=redefined-outer-name


def test_simple(qitoolchain_action):
    foo_tc = qitoolchain_action("create", "foo")
    assert foo_tc.packages == list()


def test_git_feed(qitoolchain_action, git_server, feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.44")
    feed.add_package(boost_package)
    git_server.create_repo("toolchains.git")
    git_server.change_branch("toolchains.git", "devel")
    git_server.push_file("toolchains.git", "feeds/foo.xml", feed.feed_xml.read(),
                         branch="devel")
    feed_url = git_server.get_repo("toolchains.git").clone_url

    qitoolchain_action("create", "--feed-name", "foo", "--branch", "devel", "foo", feed_url)

    new_boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.55")
    feed.add_package(new_boost_package)
    git_server.push_file("toolchains.git", "feeds/foo.xml", feed.feed_xml.read(),
                         branch="devel")

    qitoolchain_action("update", "foo")
    foo_tc = qitoolchain.get_toolchain("foo")
    assert foo_tc.get_package("boost").version == "1.55"
