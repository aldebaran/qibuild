# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import qitoolchain.qipackage

from qisrc.test.conftest import git_server  # pylint: disable=unused-import

# pylint: disable=redefined-outer-name


def test_update_local_ctc(qitoolchain_action, tmpdir):
    ctc_path = tmpdir.join("ctc").ensure(dir=True)
    ctc_path.join("toolchain.xml").write("""
<toolchain>
 <package name="ctc"
          directory="."
 />
</toolchain>
""")
    toolchain_xml = ctc_path.join("toolchain.xml")
    qitoolchain_action("create", "ctc", toolchain_xml.strpath)
    qitoolchain_action("update", "ctc", toolchain_xml.strpath)
    assert ctc_path.check(dir=True)


def test_update_no_feed(qitoolchain_action):
    qitoolchain_action("create", "foo")
    error = qitoolchain_action("update", "foo", raises=True)
    assert "Could not find feed" in error


def test_udpate_all_toolchains(qitoolchain_action, feed, record_messages):
    qitoolchain_action("create", "foo", feed.url)
    qitoolchain_action("create", "bar")
    qitoolchain_action("update")
    assert record_messages.find("These toolchains will be skipped because they have no feed: bar")
    assert record_messages.find("Updating foo")


def test_switching_to_git_feed(qitoolchain_action, git_server, feed, record_messages):
    boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.44")
    feed.add_package(boost_package)
    qitoolchain_action("create", "foo", feed.feed_xml.strpath)
    toolchain_repo = git_server.create_repo("toolchains.git")
    boost_package.version = "1.45"
    feed.add_package(boost_package)
    git_server.push_file("toolchains.git", "feeds/foo.xml", feed.feed_xml.read())
    qitoolchain_action("update", "--feed-name", "foo", "foo", toolchain_repo.clone_url)
    assert record_messages.find("from 1.44 to 1.45")
    qitoolchain_action("info", "foo")
    assert record_messages.find("on master")
