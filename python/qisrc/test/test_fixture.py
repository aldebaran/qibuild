#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Fixture """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.git
from qibuild.test.conftest import TestBuildWorkTree


def test_git_server_creates_valid_urls(tmpdir, git_server):
    """ Test Git Server Creates Valid Urls """
    _origin_url = git_server.manifest.get_remote("origin").url
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.clone_url
    assert foo_url.startswith("file://")
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(foo_url)


def test_switch_manifest_branch(tmpdir, git_server):
    """ Test Switch Manifest Branch """
    git_server.switch_manifest_branch("devel")
    assert git_server.manifest_branch == "devel"
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(git_server.manifest_url, "--branch",
              git_server.manifest_branch)
    assert git.get_current_branch() == "devel"


def test_pushing_files(tmpdir, git_server):
    """ Test Pushing Fles """
    _origin_url = git_server.manifest.get_remote("origin").url
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.clone_url
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(foo_url)
    git_server.push_file("foo.git", "README", "This is foo\n")
    git.pull()
    assert foo_clone.join("README").read() == "This is foo\n"


def test_create_several_commits(git_server):
    """ Test Create Several Commits """
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "foo.txt", "change 1")
    git_server.push_file("foo.git", "foo.txt", "change 2")


def test_no_review_by_default(tmpdir, git_server):
    """ Test No Review By Default """
    foo_repo = git_server.create_repo("foo.git")
    assert foo_repo.review is False
    origin = git_server.manifest.get_remote("origin")
    assert origin.review is False


def test_create_review_repos(tmpdir, git_server):
    """ Test Create Review Repos """
    foo_repo = git_server.create_repo("foo", review=True)
    assert foo_repo.review_remote.name == "gerrit"
    assert foo_repo.default_remote.name == "origin"
    git = qisrc.git.Git(tmpdir.strpath)
    rc, _out = git.call("ls-remote", foo_repo.clone_url, raises=False)
    assert rc == 0


def test_create_empty_repo(tmpdir, git_server):
    """ Test Create Empty Repo """
    foo_repo = git_server.create_repo("foo", empty=True)
    git = qisrc.git.Git(tmpdir.strpath)
    rc, out = git.call("ls-remote", foo_repo.clone_url, raises=False)
    assert rc == 0
    assert not out


def test_new_project_under_review(tmpdir, git_server):
    """ Test New Project Under Review """
    foo_repo = git_server.create_repo("foo.git", review=False)
    assert foo_repo.review is False
    git_server.use_review("foo.git")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.review is True
    assert foo_repo.review_remote.name == "gerrit"
    git = qisrc.git.Git(tmpdir.strpath)
    rc, _out = git.call("ls-remote", foo_repo.clone_url, raises=False)
    assert rc == 0
    git = qisrc.git.Git(tmpdir.strpath)
    rc, _out = git.call("ls-remote", foo_repo.review_remote.url, raises=False)
    assert rc == 0


def test_add_build_project(git_server, qisrc_action):
    """ Test Add Build Project """
    git_server.add_qibuild_test_project("world")
    qisrc_action("init", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    assert build_worktree.get_build_project("world")


def test_change_branch(git_server):
    """ Test Change Branch """
    git_server.create_repo("foo.git")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.default_branch == "master"
    git_server.change_branch("foo.git", "devel")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.default_branch == "devel"


def test_fixed_ref(git_server):
    """ Test Fixed Ref """
    git_server.create_repo("foo.git")
    git_server.set_fixed_ref("foo.git", "v0.1")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.default_branch is None
    assert foo_repo.fixed_ref == "v0.1"


def test_create_svn_repo(svn_server, tmpdir):
    """ Test Create SVN Repo """
    foo_url = svn_server.create_repo("foo")
    work = tmpdir.mkdir("work")
    svn = qisrc.svn.Svn(work.strpath)
    svn.call("checkout", foo_url)
    foo1 = work.join("foo")
    foo1.check(dir=True)


def test_svn_commit(svn_server, tmpdir):
    """ Test SVN Commit """
    foo_url = svn_server.create_repo("foo")
    svn_server.commit_file("foo", "README.txt", "this is a readme\n")
    work = tmpdir.mkdir("work")
    svn = qisrc.svn.Svn(work.strpath)
    svn.call("checkout", foo_url)
    foo1 = work.join("foo")
    readme = foo1.join("README.txt")
    assert readme.read() == "this is a readme\n"
