import pytest

from qisys.remote import URL, URLParseError

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
    with pytest.raises(URLParseError) as e:
        URL("foo")
