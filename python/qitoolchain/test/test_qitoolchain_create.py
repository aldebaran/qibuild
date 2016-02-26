## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisys.archive
import qisys.remote
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

    qitoolchain_action("create", "--feed-name", "foo", "--branch", "devel", "foo", feed_url)

    new_boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.55")
    feed.add_package(new_boost_package)
    git_server.push_file("toolchains.git", "feeds/foo.xml", feed.feed_xml.read(),
                         branch="devel")

    qitoolchain_action("update", "foo")
    foo_tc = qitoolchain.get_toolchain("foo")
    assert foo_tc.get_package("boost").version == "1.55"

def test_incorrect_feed_name(qitoolchain_action, git_server):
    toolchain_repo = git_server.create_repo("toolchains.git")
    feed_url = toolchain_repo.clone_url
    git_server.push_file("toolchains.git", "feeds/win32-vs2013.xml", "<toolchain />")
    error = qitoolchain_action("create", "--name", "win32-vs2015",
                               "foo", feed_url, raises=True)
    expected = "No file named feeds/win32-vs2015.xml in %s" % feed_url
    assert error == expected

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

def test_switching_from_git_feed(qitoolchain_action, git_server, tmpdir):
    git_server.create_repo("toolchains.git")
    git_server.push_file("toolchains.git", "feeds/foo.xml", "<toolchain />")
    feed_url = git_server.get_repo("toolchains.git").clone_url
    qitoolchain_action("create", "--feed-name", "foo", "foo", feed_url)
    feed_xml = tmpdir.join("feed.xml")
    feed_xml.write("<toolchain />")
    qitoolchain_action("create", "foo", feed_xml.strpath)

def test_using_feed_name_from_regular_location(qitoolchain_action, tmpdir):
    feed_path = tmpdir.join("toolchain.xml")
    feed_path.write(""" \
<toolchain>
  <feed name="bar" />
</toolchain>
""")
    error = qitoolchain_action("create", "foo", feed_path.strpath, raises=True)
    assert "Cannot use feed names with non-git URL" in error

def test_non_strict_feed_parsing(qitoolchain_action, tmpdir):
    # This test is Aldebaran-specific: We have broken feeds
    # (where package.xml of the packages and metadata in the feed
    # do not match) in production, and we need backward-compatibily
    # on this ....
    foo = tmpdir.mkdir("foo")
    foo.join("package.xml").write('<package name="foo" version="0.1" />')
    foo_archive = qisys.archive.compress(foo.strpath, flat=True)
    feed = tmpdir.join("feed.xml")
    feed.write("""
<toolchain strict_metadata="false">
 <package name="libfoo" version="0.2" url="{foo_url}" />
</toolchain>
""".format(foo_url=qisys.remote.local_url(foo_archive)))
    qitoolchain_action("create", "tc", feed.strpath)
