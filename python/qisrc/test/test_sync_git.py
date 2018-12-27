#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Sync Git """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

from qisrc.git_config import Branch


def create_foo(git_server, tmpdir, test_git):
    """ Create Foo """
    foo_git = test_git(tmpdir.join("foo").strpath)
    foo_repo = git_server.create_repo("foo.git")
    foo_git.clone(foo_repo.clone_url)
    return foo_git


def test_up_to_date(git_server, tmpdir, test_git):
    """ Test Up To Date """
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    foo_git.sync_branch(branch)


def test_fast_forward(git_server, tmpdir, test_git):
    """ Test Fast Forward """
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master")
    foo_git.sync_branch(branch)
    assert foo_git.get_current_branch() == "master"
    assert foo_git.read_file("README") == "README on master"


def test_rebase_by_default(git_server, tmpdir, test_git):
    """ Test Rebase By Default """
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master")
    foo_git.commit_file("bar", "bar on master")
    foo_git.sync_branch(branch)
    assert foo_git.get_current_branch() == "master"
    assert foo_git.read_file("README") == "README on master"
    assert foo_git.read_file("bar") == "bar on master"
    rc, head = foo_git.call("show", "HEAD", raises=False)
    assert rc == 0
    assert "Merge" not in head


def test_skip_if_unclean(git_server, tmpdir, test_git):
    """ Test Skip If UnClean """
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master")
    foo_git.sync_branch(branch)
    foo_git.root.join("README").write("changing README")
    (res, message) = foo_git.sync_branch(branch)
    assert foo_git.read_file("README") == "changing README"
    assert res is None
    assert "unstaged changes" in message


def test_do_not_call_rebase_abort_when_reset_fails(git_server, tmpdir, test_git):
    """ Test Do Not Call Rebase Abort When Reset Fails """
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master")
    foo_path = foo_git.repo
    index_lock = os.path.join(foo_path, ".git", "index.lock")
    with open(index_lock, "w") as fp:
        fp.write("")
    (res, message) = foo_git.sync_branch(branch)
    assert res is False
    assert "rebase --abort" not in message


def test_push_nonfastforward(git_server, tmpdir, test_git):
    """ Test Push No Fast Forward """
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master v1")
    foo_git.sync_branch(branch)
    git_server.push_file("foo.git", "README", "README on master v2",
                         fast_forward=False)
    (res, _message) = foo_git.sync_branch(branch)
    assert res is True
    assert foo_git.read_file("README") == "README on master v2"


def test_run_abort_when_rebase_fails(git_server, tmpdir, test_git):
    """ Test Run Abort When Rebase Fails """
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master v1")
    foo_git.sync_branch(branch)
    git_server.push_file("foo.git", "README", "README on master v2",
                         fast_forward=False)
    foo_git.commit_file("unrelated.txt", "Unrelated changes")
    (res, message) = foo_git.sync_branch(branch)
    assert res is False
    assert foo_git.get_current_branch() is not None
    assert "Rebase failed" in message
    assert foo_git.read_file("unrelated.txt") == "Unrelated changes"
    assert foo_git.read_file("README") == "README on master v1"


def test_fail_if_empty(tmpdir, test_git):
    """ Test Fail If Empty """
    foo_git = test_git(tmpdir.strpath)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    foo_git.set_tracking_branch("master", "origin")  # repo empty: fails
    (res, message) = foo_git.sync_branch(branch)
    assert res is None
    assert "no commits" in message


def test_clean_error_when_fetch_fails(git_server, tmpdir, test_git):
    """ Test Clean Error When Fetch Fails """
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master")
    git_server.srv.remove()
    res, message = foo_git.sync_branch(branch)
    assert res is False
    assert "Fetch failed" in message
