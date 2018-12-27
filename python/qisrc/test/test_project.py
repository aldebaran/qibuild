#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import copy

import qisrc.git
from qisrc.git_config import Remote, Branch
from qisrc.manifest import RepoConfig
from qisrc.test.conftest import TestGitWorkTree


def test_native_paths(git_worktree):
    """ Test Native Path """
    foo1 = git_worktree.create_git_project("foo/bar")
    assert os.path.exists(foo1.path)
    if os.name == 'nt':
        assert "/" not in foo1.path


def test_apply_git_config(git_worktree):
    """ Test Appli Git Config """
    foo1 = git_worktree.create_git_project("foo")
    upstream = Remote()
    upstream.name = "upstream"
    upstream.url = "git@srv:bar.git"
    foo1.configure_remote(upstream)
    foo1.apply_config()
    git = qisrc.git.Git(foo1.path)
    assert git.get_config("remote.upstream.url") == "git@srv:bar.git"
    foo1.configure_branch("master", tracks="upstream")
    foo1.apply_config()
    assert git.get_tracking_branch("master") == "upstream/master"
    foo1.configure_branch(
        "feature", tracks="upstream",
        remote_branch="remote_branch"
    )
    foo1.apply_config()
    assert git.get_tracking_branch("feature") == "upstream/remote_branch"


def test_branch_without_remote(git_worktree):
    """ Test Branch Without Remote """
    foo1 = git_worktree.create_git_project("foo")
    branch = Branch()
    branch.name = "master"
    branch.default = True
    foo1.branches = [branch]
    foo1.apply_config()


def test_apply_remote_config(git_worktree):
    """ Test Appli Remote Config """
    foo1 = git_worktree.create_git_project("foo")
    origin = Remote()
    origin.name = "origin"
    origin.url = "git@git:foo.git"
    origin.default = True
    gerrit = Remote()
    gerrit.name = "gerrit"
    gerrit.url = "git@review:foo.git"
    gerrit.review = True
    foo_repo = RepoConfig()
    foo_repo.remotes = [origin, gerrit]
    foo_repo.default_branch = "master"
    foo1.read_remote_config(foo_repo)
    foo1.apply_config()
    foo1.save_config()
    assert foo_repo.default_remote == origin
    assert foo1.review_remote == gerrit
    # Check its persistent:
    git_worktree = TestGitWorkTree()
    foo2 = git_worktree.get_git_project("foo")
    assert foo2.default_remote == origin
    assert foo2.review_remote == gerrit


def test_warn_on_remote_change(git_worktree, record_messages):
    """ Test Warn On Remote Change """
    foo1 = git_worktree.create_git_project("foo")
    origin = Remote()
    origin.name = "origin"
    origin.url = "git@srv:foo.git"
    foo1.configure_remote(origin)
    foo1.configure_branch("master", tracks="origin", default=True)
    origin2 = Remote()
    origin2.name = "origin"
    origin2.url = "git@srv:libfoo.git"
    foo1.configure_remote(origin2)
    assert record_messages.find("remote url changed")
    foo1.configure_branch("next", default=True)
    assert record_messages.find("default branch changed")
    gerrit = Remote()
    gerrit.name = "gerrit"
    gerrit.url = "http://gerrit/libfoo.git"
    foo1.configure_remote(gerrit)
    foo1.configure_branch("next", tracks="gerrit")
    assert record_messages.find("now tracks gerrit instead")


def test_warn_on_default_change(git_worktree, record_messages):
    """ Test Warn on Default Change """
    foo1 = git_worktree.create_git_project("foo")
    gitorious = Remote()
    gitorious.name = "gitorious"
    gitorious.url = "git@gitorious:libfoo/libfoo.git"
    gitorious.default = True
    gitlab = Remote()
    gitlab.name = "gitlab"
    gitlab.url = "git@gitlab:foo/libfoo.git"
    foo_repo = RepoConfig()
    foo_repo.default_branch = "master"
    foo_repo.remotes = [gitlab, gitorious]
    foo1.read_remote_config(foo_repo)
    foo1.apply_config()
    assert foo1.default_remote.name == "gitorious"
    gitorious2 = copy.copy(gitorious)
    gitorious2.default = False
    gitlab2 = copy.copy(gitlab)
    gitlab2.default = True
    record_messages.reset()
    foo_repo = RepoConfig()
    foo_repo.remotes = [gitlab2, gitorious2]
    foo_repo.default_branch = "master"
    foo1.read_remote_config(foo_repo)
    foo1.apply_config()
    assert record_messages.find("Default remote changed")
    assert foo1.default_remote.name == "gitlab"


def test_no_default_branch(git_worktree):
    """ Test No Default Branch """
    foo_project = git_worktree.create_git_project("foo")
    foo_repo = RepoConfig()
    foo_project.read_remote_config(foo_repo)
    foo_project.apply_config()


def test_setting_default_branch(git_worktree):
    """ Test Setting Default Branch """
    foo1 = git_worktree.create_git_project("foo")
    foo1.configure_branch("master", default=False)
    assert foo1.default_branch is None
    foo1.configure_branch("master", default=True)
    assert foo1.default_branch.name == "master"


def test_change_default_branch(git_worktree):
    """ Test Change Default Branch """
    foo_proj = git_worktree.create_git_project("foo")
    foo_proj.configure_branch("master", default=True)
    foo_proj.configure_branch("devel", default=True)
    assert foo_proj.default_branch.name == "devel"
