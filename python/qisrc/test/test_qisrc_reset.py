#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Reset """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.sh
import qisrc.snapshot
from qisrc.test.conftest import TestGit, TestGitWorkTree


def test_reset_dash_f_simple(qisrc_action, git_server):
    """ Test Reset Dash f Simple """
    git_server.create_repo("foo")
    manifest_url = git_server.manifest_url
    git_worktree = qisrc_action.git_worktree
    tmpdir = qisrc_action.tmpdir
    git_worktree.configure_manifest(manifest_url)
    snapshot = tmpdir.join("snapshot").strpath
    qisrc.snapshot.generate_snapshot(git_worktree,
                                     snapshot,
                                     deprecated_format=False)
    qisrc_action("reset", "--snapshot", snapshot, "--force")


def test_reset_undo_local_changes(qisrc_action, git_server):
    """ Test Reset Undo Local Changes """
    git_server.create_repo("foo")
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    orig_gitinore = foo_git.read_file(".gitignore")
    foo_git.root.join(".gitignore").write("new line\n")
    qisrc_action("reset", "--force")
    assert foo_git.read_file(".gitignore") == orig_gitinore


def test_reset_non_overlapping_groups(qisrc_action, git_server, tmpdir):
    """ Test Reset Non Overlapping Groups """
    git_server.create_group("group1", ["foo", "bar"])
    git_server.create_group("group2", ["spam"])
    git_worktree = qisrc_action.git_worktree
    manifest_url = git_server.manifest_url
    git_server.push_file("spam", "new", "this is new\n")
    git_worktree.configure_manifest(manifest_url)
    snapshot = tmpdir.join("snapshot").strpath
    qisrc.snapshot.generate_snapshot(git_worktree,
                                     snapshot,
                                     deprecated_format=False)
    spam_project = git_worktree.get_git_project("spam")
    git = qisrc.git.Git(spam_project.path)
    git.reset("--hard", "HEAD~1")
    old_ref = git.get_ref_sha1("refs/heads/master")
    qisrc_action("reset", "--snapshot", snapshot, "--force", "--group", "group1")
    qisrc_action("reset", "--snapshot", snapshot, "--force", "--group", "group2")
    new_ref = git.get_ref_sha1("refs/heads/master")
    assert old_ref != new_ref


def test_reset_clone_missing(qisrc_action, git_server):
    """ Test Reset Clone Missing """
    git_server.create_repo("foo")
    manifest_url = git_server.manifest_url
    git_worktree = qisrc_action.git_worktree
    tmpdir = qisrc_action.tmpdir
    git_worktree.configure_manifest(manifest_url)
    snapshot = tmpdir.join("snapshot").strpath
    qisrc.snapshot.generate_snapshot(git_worktree,
                                     snapshot,
                                     deprecated_format=False)
    foo_project = git_worktree.get_git_project("foo")
    qisys.sh.rm(foo_project.path)
    qisrc_action("reset", "--snapshot", snapshot, "--force")
    assert os.path.exists(foo_project.path)


def test_fails_when_cloning_fails(qisrc_action, git_server):
    """ Test Reset When Cloning Fails """
    git_server.create_repo("foo")
    manifest_url = git_server.manifest_url
    git_worktree = qisrc_action.git_worktree
    tmpdir = qisrc_action.tmpdir
    git_worktree.configure_manifest(manifest_url)
    snapshot = tmpdir.join("snapshot").strpath
    qisrc.snapshot.generate_snapshot(git_worktree,
                                     snapshot,
                                     deprecated_format=False)
    foo_project = git_worktree.get_git_project("foo")
    qisys.sh.rm(foo_project.path)
    qisys.sh.rm(git_server.root.strpath)
    error = qisrc_action("reset", "--snapshot", snapshot, "--force", raises=True)
    assert "Update failed" in error


def test_no_files_in_repo(qisrc_action, git_server):
    """ Test No Files In Repo """
    git_server.create_repo("foo")
    git_server.delete_file("foo", ".gitignore")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("reset")


def test_fixed_ref(qisrc_action, git_server):
    """ Test Fixed Ref """
    git_server.create_repo("foo.git")
    git_server.push_tag("foo.git", "v0.1")
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.commit_file("a.txt", "a", "test")
    qisrc_action("reset")
    _, actual = git.call("rev-parse", "HEAD", raises=False)
    _, expected = git.call("rev-parse", "v0.1", raises=False)
    assert actual == expected


def test_ignore_groups(qisrc_action, git_server):
    """ Test Ignore Group """
    git_server.create_group("a", ["a.git"])
    git_server.create_group("b", ["b.git"])
    qisrc_action("init", git_server.manifest_url,
                 "--group", "a",
                 "--group", "b")
    snapshot = qisrc_action("snapshot")
    qisrc_action("rm-group", "b")
    qisrc_action("reset", "--snapshot", snapshot, "--ignore-groups")
    git_worktree = TestGitWorkTree()
    # Check that 'b' group was not re-added
    assert len(git_worktree.git_projects) == 1
