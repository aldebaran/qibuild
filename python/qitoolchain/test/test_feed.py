#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

from qisrc.test.conftest import git_server
from qitoolchain.feed import is_url, tree_from_feed, ToolchainFeedParser

default_oss_xml = """<feed>\n    <package name="boost" url="boost.zip" />\n</feed>\n"""
default_third_part_xml = """<feed>\n  <package name="oracle-jdk" url="jdk.zip" />\n</feed>\n"""

# feed url is either absolute or relative to the parent feed url
default_full_xml = """<feed>
    <feed url="oss.xml" />
    <feed url="3rdpart.xml" />
</feed>\n"""


def test_is_url():
    """ Test is_url """
    assert not is_url(r"c:\foo\bar")
    assert is_url("http://foo.com/bar.xml")
    assert is_url("ftp://foo.com.bar.xml")
    assert is_url("file:///tmp/bar.xml")


def test_parse_non_exising_path():
    """ Test Parse non Existing Path """
    with pytest.raises(Exception) as e:
        tree_from_feed("does/not/exists")
    assert "not an existing path" in str(e)
    assert "nor an url" in str(e)


def _generic_test_git(git_server, _feed, full_xml, oss_xml, third_part_xml):
    """ Generic Git Test """
    git_server.create_repo("toolchains.git")
    git_server.push_file("toolchains.git", "feeds/oss.xml", oss_xml)
    git_server.push_file("toolchains.git", "feeds/3rdpart.xml", third_part_xml)
    git_server.push_file("toolchains.git", "feeds/full.xml", full_xml)
    git_url = git_server.get_repo("toolchains.git").clone_url
    parser = ToolchainFeedParser("foo")
    parser.parse(git_url, name="full", branch="master")
    names = [x.name for x in parser.packages]
    assert names == ["boost", "oracle-jdk"]


def test_git(git_server, feed):
    """ Test Git """
    _generic_test_git(git_server, feed, default_full_xml, default_oss_xml, default_third_part_xml)


def test_git_missing_url(git_server, feed):
    """ Test Git Missing Url """
    full_xml = """<feed>\n    <feed />\n    <feed url="3rdpart.xml" />\n</feed>\n"""
    with pytest.raises(Exception) as e:
        _generic_test_git(git_server, feed, full_xml, default_oss_xml, default_third_part_xml)
    assert "not parse" in str(e)
    assert "Non-root 'feed' element must have an 'url' attribute" in str(e)


def test_git_bad_url(git_server, feed):
    """ Test Git Bad Url """
    # URL is bad because relative url are relative to the parent URL, and this one will add one more 'feeds' prefix.
    # The resulting built URL will end with share/qi/toolchains/foo.git/feeds/feeds/3rdpart.xml
    # and the double feeds/feeds/ makes it unknown
    full_xml = """<feed>
<feed url="feeds/3rdpart.xml" />
</feed>\n"""
    with pytest.raises(Exception) as e:
        _generic_test_git(git_server, feed, full_xml, default_oss_xml, default_third_part_xml)
    assert "not parse" in str(e)
    assert "not an existing path" in str(e)
    assert "nor an url" in str(e)


def _generic_test_local(tmpdir, full_xml):
    """ Test creating a toolchain from path to a local feed xml """
    d = tmpdir.mkdir("feeds")
    p = d.join("oss.xml")
    p.write(default_oss_xml)
    p = d.join("full.xml")
    p.write(full_xml)

    parser = ToolchainFeedParser("foo")
    # Note: passing the `branch` param is quite unexpected for a local feed,
    # but it is what qitoolchain does in real life.
    parser.parse(str(p), branch="master")
    names = [x.name for x in parser.packages]
    assert names == ["boost"]


def test_local_relative_url(tmpdir):
    """ Test creating a toolchain from path to a local feed xml """
    full = '<feed>\n<feed url="oss.xml" />\n</feed>\n'
    _generic_test_local(tmpdir, full)


def test_local_file_url(tmpdir):
    """ Test creating a toolchain from path to a local feed xml """
    full = '<feed>\n<feed url="file://' + str(tmpdir) + '/feeds/oss.xml" />\n</feed>\n'
    print(tmpdir)
    print(full)
    _generic_test_local(tmpdir, full)


def test_local_bad_relative_url(tmpdir):
    """ Test creating a toolchain from path to a local feed xml """
    full = '<feed>\n<feed url="feed/oss.xml" />\n</feed>\n'
    with pytest.raises(Exception) as e:
        _generic_test_local(tmpdir, full)
    assert "not parse" in str(e)
    assert "not an existing path" in str(e)
    assert "nor an url" in str(e)


def test_local_missing_url(tmpdir):
    """ Test creating a toolchain from path to a local feed xml """
    full = '<feed>\n<feed />\n</feed>\n'
    with pytest.raises(Exception) as e:
        _generic_test_local(tmpdir, full)
    assert "not parse" in str(e)
    assert "Non-root 'feed' element must have an 'url' attribute" in str(e)
