## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import pytest

import qisys.sh
import qisrc.snapshot

def test_reset_dash_f_simple(qisrc_action, git_server):
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

def test_reset_non_overlapping_groups(qisrc_action, git_server, tmpdir):
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
