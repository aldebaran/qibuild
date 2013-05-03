import qisys.script
import qisys.sh
from qisrc.test.conftest import TestGitWorkTree

import pytest

def test_in_new_directory(cd_to_tmpdir, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisys.script.run_action("qisrc.actions.init", [git_server.manifest_url])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2

def test_no_manifest(cd_to_tmpdir):
    qisys.script.run_action("qisrc.actions.init")

def test_fails_when_not_empty(cd_to_tmpdir):
    cd_to_tmpdir.mkdir(".qi")
    with pytest.raises(Exception) as e:
        qisys.script.run_action("qisrc.actions.init")
    assert "empty directory" in str(e.value)
