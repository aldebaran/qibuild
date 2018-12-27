#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Git Config """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import mock

from qisrc.git_config import Remote


def test_url_filepath():
    """ Test Url FilePath """
    remote = Remote()
    remote.url = "file:///path/to/dir"
    remote.parse_url()
    assert remote.prefix == "file:///path/to/dir/"
    assert remote.protocol == "file"


def test_url_win_filepath():
    """ Test Url Win FilePath """
    if not os.name == 'nt':
        return
    remote = Remote()
    remote.url = r"file:///c:\path\to\foo"
    remote.parse_url()
    assert remote.prefix == r"file:///c:\path\to\foo" + "\\"
    assert remote.protocol == "file"


def test_url_git():
    """ Test Url Git """
    remote = Remote()
    remote.url = "git://example.com"
    remote.parse_url()
    assert remote.prefix == "git://example.com/"
    assert remote.protocol == "git"
    assert remote.server == "example.com"


def test_url_http():
    """ Test Url Http """
    remote = Remote()
    remote.url = "http://review.corp:8080"
    remote.parse_url()
    assert remote.prefix == "http://review.corp:8080/"
    assert remote.server == "review.corp"
    assert remote.port == 8080
    assert remote.protocol == "http"


def test_url_https_trailing_slash():
    """ Test Url Https Tailing Slash """
    remote = Remote()
    remote.url = "https://review.corp/"
    remote.parse_url()
    assert remote.prefix == "https://review.corp/"
    assert remote.server == "review.corp"
    assert remote.protocol == "https"
    assert not remote.port


def test_ssh_url():
    """ Test Ssh Url """
    remote = Remote()
    remote.url = "git@example.com"
    remote.parse_url()
    assert remote.prefix == "git@example.com:"
    assert remote.server == "example.com"
    assert remote.protocol == "ssh"
    assert not remote.port


def test_url_ssh_no_username():
    """ Test Url Ssh No Username """
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
    """ Test Gerrit Url Ssh SubFolder """
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
    """ Test Url Ssh With Username No SubFolder """
    remote = Remote()
    remote.url = "ssh://git@foo/"
    remote.parse_url()
    assert remote.prefix == "ssh://git@foo/"
    assert remote.username == "git"


def test_url_ssh_with_username_with_subfolder():
    """ Test Url Ssh With Username With SubFolder """
    remote = Remote()
    remote.url = "ssh://git@foo/bar/baz"
    remote.parse_url()
    assert remote.prefix == "ssh://git@foo/bar/baz/"
    assert remote.server == "foo"
    assert remote.username == "git"


def test_existing_path(tmpdir):
    """ Test Existing Path """
    remote = Remote()
    url = tmpdir.mkdir("srv").strpath
    remote.url = url
    remote.parse_url()
    assert remote.prefix == url + os.path.sep
