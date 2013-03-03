import qisys.script
import qisys.sh

import pytest

def test_in_new_directory(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    assert len(qisrc_action.git_worktree.git_projects) == 2

def test_no_manifest(qisrc_action):
    qisrc_action("init")

def test_fails_when_not_empty(qisrc_action):
    qisrc_action.tmpdir.mkdir(".qi")
    error = qisrc_action("init", raises=True)
    assert "empty directory" in error
