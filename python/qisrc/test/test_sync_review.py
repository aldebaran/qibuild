#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Sync Review """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import mock

import qisrc.sync
from qisrc.test.conftest import TestGitWorkTree


def test_call_setup_review(git_worktree, git_server):
    """ Test Call Setup Review """
    git_server.create_repo("foo", review=True)
    git_server.create_repo("bar", review=False)
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    with mock.patch("qisrc.review.setup_project") as mock_setup:
        mock_setup.return_value = True
        worktree_syncer.configure_manifest(manifest_url)
    foo1 = git_worktree.get_git_project("foo")
    bar1 = git_worktree.get_git_project("bar")
    assert foo1.review is True
    assert bar1.review is False
    assert mock_setup.call_count  # == 1
    # Make sure setting is persistent:
    git_worktree2 = TestGitWorkTree()
    foo1 = git_worktree2.get_git_project("foo")
    bar1 = git_worktree2.get_git_project("bar")
    assert foo1.review is True
    assert bar1.review is False
    assert foo1.review_remote.name == "gerrit"
    assert foo1.default_remote.name == "origin"


def test_does_not_store_if_setup_fails(git_worktree, git_server):
    """ Test Does Not Store If Setup Fails """
    git_server.create_repo("foo", review=True)
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    with mock.patch("qisrc.review.setup_project") as mock_setup:
        mock_setup.return_value = False
        worktree_syncer.configure_manifest(manifest_url)
    git_worktree2 = TestGitWorkTree()
    foo1 = git_worktree2.get_git_project("foo")
    assert foo1.review is False


def test_new_project_under_code_review(git_worktree, git_server):
    """ Test New Project Under Code Review """
    git_server.create_repo("foo", review=False)
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest(manifest_url)
    foo1 = git_worktree.get_git_project("foo")
    assert foo1.review is False
    git_server.use_review("foo")
    with mock.patch("qisrc.review.setup_project") as mock_setup:
        worktree_syncer.sync()
        worktree_syncer.configure_projects()
    foo1 = git_worktree.get_git_project("foo")
    assert foo1.review is True
    assert mock_setup.called_once
