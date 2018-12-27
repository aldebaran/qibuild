#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Git """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.sh
import qisrc.git
from qisrc.test.conftest import TestGit


def test_name_from_url_common():
    """ Test Name From Url Common """
    examples = [
        ("git@git:foo/bar.git", "foo/bar.git"),
        ("/srv/git/foo/bar.git", "bar.git"),
        ("file:///srv/git/foo/bar.git", "bar.git"),
        ("ssh://git@review:29418/foo/bar.git", "foo/bar.git"),
        ("ssh://git@example.com/spam/eggs.git", "spam/eggs.git"),
        ("ssh://git@example.com/eggs.git", "eggs.git"),
        ("http://github.com/john/bar.git", "john/bar.git")
    ]
    for (url, expected) in examples:
        actual = qisrc.git.name_from_url(url)
        assert actual == expected


def test_name_from_url_win():
    """ Test Name From Url Win """
    if not os.name == 'nt':
        return
    url = r"file://c:\path\to\bar.git"
    assert qisrc.git.name_from_url(url) == "bar.git"


def test_set_tracking_branch_on_empty_repo(tmpdir):
    """ Test Set Tracking Branch On Empty Repo """
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    ret = git.set_tracking_branch("master", "master", "origin")
    assert ret is False


def test_set_tracking_branch_existing_branch_tracking_none(tmpdir):
    """ Test Set Tracking Branch Existing Branch Tracking None """
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    git.commit("-m", "empty", "--allow-empty")
    ret = git.set_tracking_branch("master", "master", "origin")
    assert ret is True


def test_set_tracking_branch_existing_branch_tracking_ok(tmpdir):
    """ Test Set Tracking Branch Existing Branch Tacking Ok """
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    git.commit("-m", "empty", "--allow-empty")
    git.set_tracking_branch("master", "origin")
    ret = git.set_tracking_branch("master", "origin")
    assert ret is True


def test_set_tracking_branch_existing_branch_tracking_other(tmpdir):
    """ Test Set Tracking Branch Existing Branch Tacking Other """
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    git.commit("-m", "empty", "--allow-empty")
    git.set_tracking_branch("master", "origin")
    ret = git.set_tracking_branch("master", "other")
    assert ret is True


def test_changelog(cd_to_tmpdir):
    """ Test Changelog """
    git = TestGit()
    git.initialize()
    message_1 = "mess1"
    git.commit_file("foo.txt", "foo\n", message=message_1)
    message_2 = "mess2"
    git.commit_file("foo.txt", "bar\n", message=message_2)
    commits = git.get_log("HEAD~2", "HEAD")
    assert len(commits) == 2
    assert commits[0]["message"] == message_1
    assert commits[1]["message"] == message_2


def test_get_repo_root(tmpdir):
    """ Test Get Repo Root """
    root = tmpdir.ensure("CrazyCase", dir=True)
    git = TestGit(root.strpath)
    git.initialize()
    subdir = root.ensure("some", "subdir", dir=True)
    actual = qisrc.git.get_repo_root(subdir.strpath)
    expected = qisys.sh.to_native_path(root.strpath)
    assert actual == expected


def test_safe_checkout(cd_to_tmpdir, git_server):
    """ Test Safe Checkout """
    git_server.create_repo("foo.git")
    git = TestGit()
    git.clone(git_server.srv.join("foo.git").strpath)
    ok, _mess = git.safe_checkout("devel", "origin")
    assert git.get_current_branch() == "devel"
    assert ok


def test_ignores_env(tmpdir, monkeypatch):
    """ Test Ignore Env """
    repo1 = tmpdir.mkdir("repo1")
    repo2 = tmpdir.mkdir("repo2")
    git1 = TestGit(repo1.strpath)
    git2 = TestGit(repo2.strpath)
    git1.initialize()
    git2.initialize()
    untracked = repo1.join("untracked")
    untracked.ensure(file=True)
    monkeypatch.setenv("GIT_DIR", repo1.join(".git").strpath)
    monkeypatch.setenv("GIT_WORK_TREE", repo1.strpath)
    git2.call("clean", "--force")
    assert untracked.check(file=1)


def test_ending_newlines(cd_to_tmpdir):
    """ Test Ending New Lines """
    git = TestGit()
    git.initialize()
    message_1 = "mess1"
    file_1 = "foo.txt"
    content_1 = "\nfoo\nbar\n\n"
    git.commit_file(file_1, content_1, message=message_1)
    # Test git subcommand which doesn't keep the last newline by default
    rc, out = git.status(raises=False)
    assert rc == 0
    assert out[-1] != "\n"
    rc, out = git.status(raises=False, keep_last_newline=True)
    assert rc == 0
    assert out[-1] == "\n"
    # Test git subcommand which KEEP the last newline by default
    rc, out = git.show("master:foo.txt", raises=False)
    assert rc == 0
    assert out[-1] == "\n"
    assert out == content_1
    rc, out = git.show("master:foo.txt", raises=False, keep_last_newline=False)
    assert rc == 0
    assert out[-1] != "\n"
    assert out != content_1
