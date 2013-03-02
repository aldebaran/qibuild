import qisys.script
import qisys.sh
import qisrc.git


import pytest

def test_sync_clones_new_repos(tmpdir, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    with qisys.sh.change_cwd(tmpdir.strpath):
        qisys.script.run_action("qisrc.actions.init", [git_server.manifest_url])
        assert not tmpdir.join("foo").join("README").check(file=True)
        git_server.push_file("foo.git", "README", "This is foo\n")
        qisys.script.run_action("qisrc.actions.sync")
        assert tmpdir.join("foo").join("README").check(file=True)

def test_sync_skips_unconfigured_projects(tmpdir, git_server, test_git):
    git_server.create_repo("foo.git")
    with qisys.sh.change_cwd(tmpdir.strpath):
        qisys.script.run_action("qisrc.actions.init", [git_server.manifest_url])
        worktree = qisys.worktree.WorkTree(tmpdir.strpath)
        git_worktree = qisrc.worktree.GitWorkTree(worktree)
        new_proj = tmpdir.mkdir("new_proj")
        git = test_git(new_proj.strpath)
        git.initialize()
        git_worktree.add_git_project(new_proj.strpath)
        qisys.script.run_action("qisrc.actions.sync")
