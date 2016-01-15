## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qitoolchain.feed import *

import qisys.error
from qisrc.test.conftest import git_server

import pytest

def test_is_url():
    assert not is_url(r"c:\foo\bar" )
    assert is_url("http://foo.com/bar.xml")
    assert is_url("ftp://foo.com.bar.xml")

def test_parse_non_exising_path():
    #pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        tree_from_feed("does/not/exists")
    assert "not an existing path" in e.value.message
    assert "nor an url" in e.value.message

def test_git(git_server, feed):
    git_server.create_repo("toolchains.git")
    oss_xml = """\
<feed>
    <package name="boost" url="boost.zip" />
</feed>
"""
    third_part_xml = """\
<feed>
  <package name="oracle-jdk" url="jdk.zip" />
</feed>
"""
    full_xml = """ \
<feed>
    <feed name="oss" />
    <feed name="3rdpart" />
</feed>
"""

    git_server.push_file("toolchains.git", "feeds/oss.xml", oss_xml)
    git_server.push_file("toolchains.git", "feeds/3rdpart.xml", third_part_xml)
    git_server.push_file("toolchains.git", "feeds/full.xml", full_xml)

    git_url = git_server.get_repo("toolchains.git").clone_url

    parser = ToolchainFeedParser("foo")
    parser.parse(git_url, name="full", branch="master")

    names = [x.name for x in parser.packages]
    assert names == ["boost", "oracle-jdk"]
