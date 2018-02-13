# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import pytest

from qitoolchain.feed import is_url, tree_from_feed, ToolchainFeedParser

from qisrc.test.conftest import git_server  # pylint: disable=unused-import

# pylint: disable=redefined-outer-name


#
# Commons variables
#
default_oss_xml = """\
<feed>
    <package name="boost" url="boost.zip" />
</feed>
"""

default_third_part_xml = """\
<feed>
  <package name="oracle-jdk" url="jdk.zip" />
</feed>
"""

# feed url is either absolute or relative to the parent feed url
default_full_xml = """ \
<feed>
    <feed name="oss" path="feeds/oss.xml" />
    <feed name="3rdpart" url="3rdpart.xml" />
</feed>
"""


def test_is_url():
    assert not is_url(r"c:\foo\bar")
    assert is_url("http://foo.com/bar.xml")
    assert is_url("ftp://foo.com.bar.xml")


def test_parse_non_exising_path():
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        tree_from_feed("does/not/exists")
    assert "not an existing path" in e.value.message
    assert "nor an url" in e.value.message


def _generic_test_git(_git_server, _feed, full_xml, oss_xml, third_part_xml):
    _git_server.create_repo("toolchains.git")

    _git_server.push_file("toolchains.git", "feeds/oss.xml", oss_xml)
    _git_server.push_file("toolchains.git", "feeds/3rdpart.xml", third_part_xml)
    _git_server.push_file("toolchains.git", "feeds/full.xml", full_xml)

    git_url = _git_server.get_repo("toolchains.git").clone_url

    parser = ToolchainFeedParser("foo")
    parser.parse(git_url, name="full", branch="master")

    names = [x.name for x in parser.packages]
    assert names == ["boost", "oracle-jdk"]


def test_git(git_server, feed):
    _generic_test_git(git_server, feed, default_full_xml, default_oss_xml, default_third_part_xml)


def test_git_missing_url_and_path(git_server, feed):
    full_xml = """ \
<feed>
    <feed name="oss" />
    <feed name="3rdpart" url="3rdpart.xml" />
</feed>
"""
    with pytest.raises(AssertionError) as e:
        _generic_test_git(git_server, feed, full_xml, default_oss_xml, default_third_part_xml)
    assert "attributes must be set" in e.value.message
    assert "url" in e.value.message
    assert "path" in e.value.message


def test_git_bad_url(git_server, feed):
    # URL is bad because relative url are relative to the parent URL, and this one will add one more 'feeds' prefix.
    # The resulting built URL will end with share/qi/toolchains/foo.git/feeds/feeds/3rdpart.xml
    # and the double feeds/feeds/ makes it unknown
    full_xml = """ \
<feed>
    <feed name="oss" path="feeds/oss.xml" />
    <feed name="3rdpart" url="feeds/3rdpart.xml" />
</feed>
"""

    with pytest.raises(Exception) as e:
        _generic_test_git(git_server, feed, full_xml, default_oss_xml, default_third_part_xml)
    assert "not parse" in e.value.message
    assert "not an existing path" in e.value.message
    assert "nor an url" in e.value.message
