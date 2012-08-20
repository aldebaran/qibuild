## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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


def test_push(tmpdir):
    foo_url = create_git_repo(tmpdir.strpath, "foo")
    work = tmpdir.mkdir("work")
    foo_src = work.mkdir("foo")
    foo_src = foo_src.strpath
    git = qisrc.git.Git(foo_src)
    git.clone(foo_url)

    # this should work:
    qisrc.review.push(foo_src, "master")
    (retcode, out) = git.call("ls-remote", "origin", raises=False)
    assert retcode == 0
    assert "refs/for/master" not in out
    assert "refs/heads/master" in out

    gerrit_url = create_git_repo(tmpdir.strpath, "foo-gerrit")
    git.call("remote", "add", "gerrit", gerrit_url)
    git.set_config("review.remote", "gerrit")
    git.checkout("-b", "next")
    qisrc.review.push(foo_src, "next")
    (retcode, out) = git.call("ls-remote", "gerrit", raises=False)
    assert retcode == 0
    assert "refs/for/next" in out
    assert "refs/heads/next" not in out
