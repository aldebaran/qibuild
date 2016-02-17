## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

from qisrc.git_config import Remote
import qisrc.review

import mock

def test_url_filepath():
    remote = Remote()
    remote.url = "file:///path/to/dir"
    remote.parse_url()
    assert remote.prefix == "file:///path/to/dir/"
    assert remote.protocol == "file"

def test_url_win_filepath():
    if not os.name == 'nt':
        return
    remote = Remote()
    remote.url = r"file:///c:/path/to/foo"
    remote.parse_url()
    assert remote.prefix == r"file:///c:/path/to/foo/"
    assert remote.protocol == "file"

def test_url_git():
    remote = Remote()
    remote.url = "git://example.com"
    remote.parse_url()
    assert remote.prefix == "git://example.com/"
    assert remote.protocol == "git"
    assert remote.server == "example.com"

def test_url_http():
    remote = Remote()
    remote.url = "http://review.corp:8080"
    remote.parse_url()
    assert remote.prefix == "http://review.corp:8080/"
    assert remote.server == "review.corp"
    assert remote.port == 8080
    assert remote.protocol == "http"

def test_url_https_trailing_slash():
    remote = Remote()
    remote.url = "https://review.corp/"
    remote.parse_url()
    assert remote.prefix == "https://review.corp/"
    assert remote.server == "review.corp"
    assert remote.protocol == "https"
    assert not remote.port

def test_ssh_url():
    remote = Remote()
    remote.url = "git@example.com"
    remote.parse_url()
    assert remote.prefix == "git@example.com:"
    assert remote.server == "example.com"
    assert remote.protocol == "ssh"
    assert not remote.port

def test_url_ssh_no_username():
    with mock.patch("qisrc.review.get_gerrit_username") as get_username:
        get_username.return_value = "john"
        remote = Remote()
        remote.url = "ssh://review.corp:29418"
        remote.parse_url()
        assert remote.prefix == "ssh://john@review.corp:29418/"
        assert remote.server == "review.corp"
        assert remote.port == 29418
        assert remote.protocol == "ssh"
        assert remote.username == "john"

def test_gerrit_url_ssh_subfolder():
    with mock.patch("qisrc.review.get_gerrit_username") as get_username:
        get_username.return_value = "john"
        remote = Remote()
        remote.url = "ssh://review.corp:29418/a/subfolder"
        remote.parse_url()
        assert remote.prefix == "ssh://john@review.corp:29418/a/subfolder/"
        assert remote.port == 29418
        remote.url = "ssh://review.corp:29418/a/subfolder/"
        remote.parse_url()
        assert remote.prefix == "ssh://john@review.corp:29418/a/subfolder/"

def test_url_ssh_with_username_no_subfolder():
    remote = Remote()
    remote.url = "ssh://git@foo/"
    remote.parse_url()
    assert remote.prefix == "ssh://git@foo/"
    assert remote.username == "git"

def test_url_ssh_with_username_with_subfolder():
    remote = Remote()
    remote.url = "ssh://git@foo/bar/baz"
    remote.parse_url()
    assert remote.prefix == "ssh://git@foo/bar/baz/"
    assert remote.server == "foo"
    assert remote.username == "git"

def test_existing_path(tmpdir):
    remote = Remote()
    url = tmpdir.mkdir("srv").strpath
    remote.url = url
    remote.parse_url()
    assert remote.prefix == url + os.path.sep
