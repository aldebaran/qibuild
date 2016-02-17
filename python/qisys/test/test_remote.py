## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import pytest

from qisys.remote import URL, URLParseError, deploy
from qisys.test.conftest import skip_deploy

def test_simple_url():
    url = URL("foo@bar")
    assert url.as_string == "foo@bar"
    assert url.host == "bar"
    assert url.user == "foo"
    assert url.port == 22
    assert url.remote_directory is None

def test_simple_url_with_remote_dir():
    url = URL("foo@bar:deploy")
    assert url.host == "bar"
    assert url.user == "foo"
    assert url.port == 22
    assert url.remote_directory == "deploy"

def test_no_username():
    url = URL("host:dir")
    assert url.host == "host"
    assert url.remote_directory == "dir"
    assert url.port == 22
    assert not url.user

def test_modern_urls():
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
    # pylint: disable-msg=E1101
    with pytest.raises(URLParseError) as e:
        URL("foo")

@skip_deploy
def test_deploy(tmpdir):
    local = tmpdir.mkdir("local")
    remote = tmpdir.mkdir("remote")

    deploy(local.strpath, URL("ssh://localhost/" + remote.strpath))
