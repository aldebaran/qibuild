from qisrc.test.conftest import TestGitWorkTree
from qisrc.test.conftest import TestGit

def test_push_after_rebase(git_server, git_worktree, qisrc_action, interact):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    git_server.push_file("foo", "master.txt", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_server.push_file("foo", "master.txt", "master")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.commit_file("devel.txt", "devel")
    git.fetch()
    git.push("origin", "devel")
    interact.answers = [True]
    qisrc_action("rebase", "master", "--push", "--all")
    local_sha1 = git.get_ref_sha1("refs/heads/devel")
    remote_sha1 = git.get_ref_sha1("refs/remotes/origin/devel")
    assert local_sha1 == remote_sha1

def test_undo(git_server, git_worktree, qisrc_action, interact):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    git_server.push_file("foo", "master.txt", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_server.push_file("foo", "master.txt", "master")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.commit_file("devel.txt", "devel")
    git.fetch()
    git.push("origin", "devel")
    expected_sha1 = git.get_ref_sha1("refs/remotes/origin/devel")
    interact.answers = [True]
    qisrc_action("rebase", "master", "--push", "--all")
    qisrc_action("rebase", "master", "--undo", "--all")
    actual_sha1 = git.get_ref_sha1("refs/remotes/origin/devel")
    assert actual_sha1 == expected_sha1
