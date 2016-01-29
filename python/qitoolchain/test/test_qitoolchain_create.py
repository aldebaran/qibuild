## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qitoolchain.qipackage

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

from qisrc.test.conftest import git_server

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

    qitoolchain_action("create", "--name", "foo", "--branch", "devel", "foo", feed_url)

    new_boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.55")
    feed.add_package(new_boost_package)
    git_server.push_file("toolchains.git", "feeds/foo.xml", feed.feed_xml.read(),
                         branch="devel")

    qitoolchain_action("update", "foo")
    foo_tc = qitoolchain.get_toolchain("foo")
    assert foo_tc.get_package("boost").version == "1.55"

def make_local_ctc_feed(tmpdir, base_path, version):
    base_path = tmpdir.join(base_path).ensure(dir=True)
    ctc_toolchain_file = base_path.join("toolchain.cmake")
    ctc_package = qitoolchain.qipackage.QiPackage("ctc", version=version)
    ctc_package.path = base_path.strpath
    ctc_package.toolchain_file = "toolchain.cmake"
    ctc_package.write_package_xml()
    feed_xml = base_path.join("toolchain.xml")
    feed_xml.write("""
<toolchain>
   <package name="ctc" directory="." />
</toolchain>
""")
    return feed_xml

def test_upgrading_from_local_feed(qitoolchain_action, tmpdir, toolchains):
    ctc = toolchains.create("ctc")
    feed_1 = make_local_ctc_feed(tmpdir, "ctc_1", "0.1")
    ctc.update(feed_1.strpath)
    assert ctc.get_package("ctc").version == "0.1"
    feed_2 = make_local_ctc_feed(tmpdir, "ctc_2", "0.2")
    ctc.update(feed_2.strpath)
    expected = tmpdir.join("ctc_2", "toolchain.cmake")
    assert ctc.get_package("ctc").toolchain_file == expected

def test_upgrading_after_local_feed_move(qitoolchain_action, tmpdir, toolchains):
    ctc = toolchains.create("ctc")
    feed_1 = make_local_ctc_feed(tmpdir, "ctc_1", "0.1")
    ctc.update(feed_1.strpath)
    assert ctc.get_package("ctc").version == "0.1"
    feed_2 = make_local_ctc_feed(tmpdir, "ctc_2", "0.1")
    ctc.update(feed_2.strpath)
    expected = tmpdir.join("ctc_2", "toolchain.cmake")
    assert ctc.get_package("ctc").toolchain_file == expected
