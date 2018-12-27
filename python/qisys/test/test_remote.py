#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Remote """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

from qisys.remote import URL, URLParseError, deploy


def test_simple_url():
    """ Test Simple Url """
    url = URL("foo@bar")
    assert url.as_string == "foo@bar"
    assert url.host == "bar"
    assert url.user == "foo"
    assert url.port == 22
    assert url.remote_directory is None


def test_simple_url_with_remote_dir():
    """ Test Simple Url With Remote Dir """
    url = URL("foo@bar:deploy")
    assert url.host == "bar"
    assert url.user == "foo"
    assert url.port == 22
    assert url.remote_directory == "deploy"


def test_modern_urls():
    """ Test Modern Urls """
    url = URL("ssh://foo@bar/deploy")
    assert url.host == "bar"
    assert url.user == "foo"
    assert url.port == 22
    assert url.remote_directory == "deploy"
    url = URL("ssh://foo@bar")
    assert url.host == "bar"
    assert url.user == "foo"
    assert url.port == 22
    assert url.remote_directory is None
    url = URL("ssh://foo@bar:2222/deploy")
    assert url.host == "bar"
    assert url.user == "foo"
    assert url.port == 2222
    assert url.remote_directory == "deploy"


def test_errors():
    """ Test Errors """
    with pytest.raises(URLParseError):
        URL("foo")


def test_deploy(tmpdir):
    """ Test Deploy """
    local = tmpdir.mkdir("local")
    remote = tmpdir.mkdir("remote")
    deploy(local.strpath, URL("ssh://localhost/" + remote.strpath))
