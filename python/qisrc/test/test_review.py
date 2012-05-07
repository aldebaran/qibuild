## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import mock

import qibuild.interact
import qisrc.git
import qisrc.review
from qisrc.test.test_git import create_git_repo


def test_http_to_ssh():
    res = qisrc.review.http_to_ssh("http://gerrit:8080", "foo/bar.git", "john")
    assert res == "ssh://john@gerrit:29418/foo/bar.git"

    res = qisrc.review.http_to_ssh("http://gerrit", "foo/bar.git", "john")
    assert res == "ssh://john@gerrit:29418/foo/bar.git"

    res = qisrc.review.http_to_ssh("http://gerrit.example.com", "foo/bar.git", "john")
    assert res == "ssh://john@gerrit.example.com:29418/foo/bar.git"

def test_parse_git_url():
    res = qisrc.review.parse_git_url("ssh://john@gerrit:29418")
    assert res == ("john", "gerrit", "29418")

    res = qisrc.review.parse_git_url("john@gerrit:29418")
    assert res == ("john", "gerrit", "29418")

    res = qisrc.review.parse_git_url("john@gerrit")
    assert res == ("john", "gerrit", None)

    res = qisrc.review.parse_git_url("ssh://john@gerrit:29418/foo/bar.git")
    assert res == ("john", "gerrit", "29418")

    res = qisrc.review.parse_git_url("ssh://john2@bar2.baz_smap-eggs.com:42/foo/bar.git")
    assert res == ("john2", "bar2.baz_smap-eggs.com", "42")


def test_push():
    with mock.patch('qibuild.command.call') as fake_command:
        qisrc.review.push("foo", "master")
        assert fake_command.call_args[0][0] == ["git", "push", "gerrit", "master:refs/for/master"]
        fake_command.reset()
        qisrc.review.push("foo", "master", review=False)
        assert fake_command.call_args[0][0] == ["git", "push", "gerrit", "master:master"]
