#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
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
    <feed name="oss" path="feeds/oss.xml" />
    <feed name="3rdpart" url="3rdpart.xml" />
</feed>\n"""


def test_is_url():
    """ Test is_url """
    assert not is_url(r"c:\foo\bar")
    assert is_url("http://foo.com/bar.xml")
    assert is_url("ftp://foo.com.bar.xml")


def test_parse_non_exising_path():
    """ Test Parse non Existing Path """
    with pytest.raises(Exception) as e:
        tree_from_feed("does/not/exists")
    assert "not an existing path" in e.value.message
    assert "nor an url" in e.value.message


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


def test_git_missing_url_and_path(git_server, feed):
    """ Test Git Missing Url and Path """
    full_xml = """<feed>\n    <feed name="oss" />\n    <feed name="3rdpart" url="3rdpart.xml" />\n</feed>\n"""
    with pytest.raises(AssertionError) as e:
        _generic_test_git(git_server, feed, full_xml, default_oss_xml, default_third_part_xml)
    assert "attributes must be set" in e.value.message
    assert "url" in e.value.message
    assert "path" in e.value.message


def test_git_bad_url(git_server, feed):
    """ Test Git Bad Url """
    # URL is bad because relative url are relative to the parent URL, and this one will add one more 'feeds' prefix.
    # The resulting built URL will end with share/qi/toolchains/foo.git/feeds/feeds/3rdpart.xml
    # and the double feeds/feeds/ makes it unknown
    full_xml = """<feed>
<feed name="oss" path="feeds/oss.xml" />
<feed name="3rdpart" url="feeds/3rdpart.xml" />
</feed>\n"""
    with pytest.raises(Exception) as e:
        _generic_test_git(git_server, feed, full_xml, default_oss_xml, default_third_part_xml)
    assert "not parse" in e.value.message
    assert "not an existing path" in e.value.message
    assert "nor an url" in e.value.message
