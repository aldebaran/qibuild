## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.sh
import qisrc.snapshot
from qisrc.test.conftest import TestGitWorkTree

import pytest

def test_dump_load(tmpdir):
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.refs["foo"] = "a42fb"
    snapshot.refs["bar"] = "bccad"
    snapshot_txt = tmpdir.join("snapshot.txt").strpath
    snapshot.dump(snapshot_txt)
    snapshot2 = qisrc.snapshot.Snapshot()
    snapshot2.load(snapshot_txt)
    assert snapshot2 == snapshot


def test_generate_load(git_worktree, tmpdir):
    foo_proj = git_worktree.create_git_project("foo")
    foo_git = qisrc.git.Git(foo_proj.path)
    _, foo_ref_expected = foo_git.call("rev-parse", "HEAD", raises=False)
    snapshot_txt = tmpdir.join("snapshot.txt").strpath
    qisrc.snapshot.generate_snapshot(git_worktree, snapshot_txt)
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.load(snapshot_txt)
    foo_ref = snapshot.refs["foo"]

    # Make a commit and an other diff
    foo_git.commit("--message", "empty", "--allow-empty")

    qisrc.snapshot.load_snapshot(git_worktree, snapshot_txt)
    _, foo_ref_actual = foo_git.call("rev-parse", "HEAD", raises=False)

    assert foo_ref_actual == foo_ref_expected


def test_always_fetch(git_worktree, git_server, tmpdir):
    foo_repo = git_server.create_repo("foo.git")
    git_worktree.clone_missing(foo_repo)
    foo_proj = git_worktree.get_git_project("foo")
    git_server.push_file("foo.git", "other.txt", "other change\n")
    foo_git = qisrc.git.Git(foo_proj.path)
    rc, remote_sha1 = foo_git.call("ls-remote", "origin", "refs/heads/master",
                                   raises=False)
    assert rc == 0
    remote_sha1 = remote_sha1.split()[0]

    snapshot = qisrc.snapshot.Snapshot()
    snapshot.refs["foo"] = remote_sha1
    snapshot_txt = tmpdir.join("snapshot.txt").strpath
    snapshot.dump(snapshot_txt)

    qisrc.snapshot.load_snapshot(git_worktree, snapshot_txt)
    _, local_sha1 = foo_git.call("rev-parse", "HEAD", raises=False)
    assert local_sha1 == remote_sha1


def test_load_file_object(tmpdir):
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.refs["foo"] = "d34db33f"
    snapshot_txt = tmpdir.join("snap.txt").strpath
    snapshot.dump(snapshot_txt)
    snapshot2 = qisrc.snapshot.Snapshot()
    with open(snapshot_txt) as fp:
        snapshot2.load(fp)
    assert snapshot2 == snapshot

def test_load_file_path(tmpdir):
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.refs["foo"] = "d34db33f"
    snapshot_txt = tmpdir.join("snap.txt").strpath
    snapshot.dump(snapshot_txt)
    snapshot2 = qisrc.snapshot.Snapshot()
    snapshot2.load(snapshot_txt)
    assert snapshot2 == snapshot

def test_stores_manifest_in_snapshot(git_server, git_worktree):
    git_server.create_repo("foo")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest(manifest_url)
    snapshot = git_worktree.snapshot()
    manifest = snapshot.manifest
    assert manifest.url == manifest_url

def test_generate_load_json(tmpdir, git_server, git_worktree):
    snapshot1 = qisrc.snapshot.Snapshot()
    snapshot1.manifest = qisrc.sync.LocalManifest()
    snapshot1.manifest.ref = "refs/heads/master"
    snapshot1.manifest.url = "foo@example.com"
    snapshot1.refs["a"] = "dead42"
    snapshot1.refs["b"] = "dead43"
    snapshot_json = tmpdir.join("snapshot.json").strpath
    snapshot1.dump(snapshot_json, deprecated_format=False)
    snapshot2 = qisrc.snapshot.Snapshot()
    snapshot2.load(snapshot_json)
    assert snapshot2 == snapshot1

