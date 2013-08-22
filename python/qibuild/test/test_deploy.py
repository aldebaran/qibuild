## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


import pytest
import qibuild.deploy

def test_parse_url():
    res = qibuild.deploy.parse_url("john42-bar@foo.bar.com:some/really_strange-path")
    assert res == {'given': "john42-bar@foo.bar.com:some/really_strange-path",
            'login': 'john42-bar', 'url': "foo.bar.com", 'dir': 'some/really_strange-path'}
    res = qibuild.deploy.parse_url("john@foo:")
    assert res == {'given': 'john@foo:', 'login':'john', 'url':'foo', 'dir': ''}
    res = qibuild.deploy.parse_url("foo:lol")
    assert res is None

    res = qibuild.deploy.parse_url("http://login@example.com:path")
    assert res is None

    res = qibuild.deploy.parse_url("ssh://login@example.com:1234/path")
    assert res == {'given': "ssh://login@example.com:1234/path",
            'login':'login', 'url':'example.com', 'dir':'/path', 'port':1234}

def test_project_like_urls_are_parsed_as_none():
    res = qibuild.deploy.parse_url("foo")
    assert res is None

