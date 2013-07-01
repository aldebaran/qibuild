import qisys.script
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
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.script.run_action("qisrc.actions.init")
    assert "empty directory" in str(e.value)

def test_use_branch(cd_to_tmpdir, git_server):
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.create_repo("onlyindevel.git")
    qisys.script.run_action("qisrc.actions.init",
                            [git_server.manifest_url, "--branch", "devel"])

    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2

def test_finish_configure_after_error(cd_to_tmpdir, git_server):
    # bogus repo can't be configured, but we don't want configuration to be
    # interrupted
    git_server.create_repo("foo.git", review=True)
    git_server.manifest.add_repo("bogus", None, ["origin", "gerrit"])
    git_server.create_repo("bar.git", review=True)

    qisys.script.run_action("qisrc.actions.init", [git_server.manifest_url])
    git_worktree = TestGitWorkTree()
    assert git_worktree.manifests
