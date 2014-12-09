import qisys.script
from qisrc.test.conftest import TestGitWorkTree

import pytest

def test_in_new_directory(cd_to_tmpdir, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisys.script.run_action("qisrc.actions.init", [git_server.manifest_url])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2

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
    assert git_worktree.manifest

def test_reconfigure(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("c")
    qisrc_action("init",  manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3
    qisrc_action("init", manifest_url, "-g", "mygroup")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2

def setup_re_add(qisrc_action, git_server):
    """ Helper for test_re_add_projects """
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("c")
    qisrc_action("init", manifest_url)

def test_re_add_happy_path(qisrc_action, git_server):
    setup_re_add(qisrc_action, git_server)
    manifest_url =  git_server.manifest_url
    qisrc_action("init", manifest_url,"--group", "mygroup")
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3

def test_re_add_removed_by_hand(qisrc_action, git_server):
    manifest_url =  git_server.manifest_url
    setup_re_add(qisrc_action, git_server)
    git_worktree = TestGitWorkTree()
    c_path = git_worktree.get_git_project("c").path
    qisrc_action("init", manifest_url, "--group", "mygroup")
    qisys.sh.rm(c_path)
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3

def test_re_add_path_exists(qisrc_action, git_server):
    manifest_url =  git_server.manifest_url
    setup_re_add(qisrc_action, git_server)
    git_worktree = TestGitWorkTree()
    c_path = git_worktree.get_git_project("c").path
    qisrc_action("init", manifest_url, "--group", "mygroup")
    qisys.sh.rm(c_path)
    qisys.sh.mkdir(c_path)
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3

def test_stores_default_group(qisrc_action, git_server):
    git_server.create_group("default", ["a"], default=True)
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert git_worktree.manifest.groups == ["default"]
