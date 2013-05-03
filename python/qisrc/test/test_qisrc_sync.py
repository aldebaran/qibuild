import os

import py

import qisys.script
import qisys.sh
from qisrc.test.conftest import TestGitWorkTree




def test_sync_clones_new_repos(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    cwd = py.path.local(os.getcwd())
    assert not cwd.join("foo").join("README").check(file=True)
    git_server.push_file("foo.git", "README", "This is foo\n")
    qisys.script.run_action("qisrc.actions.sync")
    assert cwd.join("foo").join("README").check(file=True)

def test_sync_skips_unconfigured_projects(qisrc_action, git_server, test_git):
    git_server.create_repo("foo.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    cwd = py.path.local(os.getcwd())
    new_proj = cwd.mkdir("new_proj")
    git = test_git(new_proj.strpath)
    git.initialize()
    git_worktree.add_git_project(new_proj.strpath)
    qisys.script.run_action("qisrc.actions.sync")
