# this is only used on buildfarm, so only test this
import pytest

import qisrc.snapshot

def test_reset_dash_f(qisrc_action, git_server):
    git_server.create_repo("foo")
    manifest_url = git_server.manifest_url
    git_worktree = qisrc_action.git_worktree
    tmpdir = qisrc_action.tmpdir
    git_worktree.configure_manifest("default", manifest_url)
    snapshot = tmpdir.join("snapshot").strpath
    qisrc.snapshot.generate_snapshot(git_worktree,
                                     snapshot,
                                     deprecated_format=False)
    qisrc_action("reset", "--snapshot", snapshot, "--force")
