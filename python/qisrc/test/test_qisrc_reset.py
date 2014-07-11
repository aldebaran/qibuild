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
    rc = qisrc_action("reset", "--snapshot", snapshot, "--force", retcode=True)
    assert rc == 1

