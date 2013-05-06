import qisrc.git
from qisrc.worktree import Branch, Remote
from qisrc.test.conftest import TestGitWorkTree

import pytest

def create_foo(git_server, tmpdir, test_git):
    foo_git = test_git(tmpdir.join("foo").strpath)
    foo_repo = git_server.create_repo("foo.git")
    foo_git.clone(foo_repo.remote_url)
    return foo_git

def test_up_to_date(git_server, tmpdir, test_git):
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    foo_git.sync_branch(branch)

def test_fast_forward(git_server, tmpdir, test_git):
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master")
    foo_git.sync_branch(branch)
    assert foo_git.get_current_branch() == "master"
    assert foo_git.read_file("README") == "README on master"

def test_rebase_by_default(git_server, tmpdir, test_git):
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master")
    foo_git.commit_file("bar", "bar on master")
    foo_git.sync_branch(branch)
    assert foo_git.get_current_branch() == "master"
    assert foo_git.read_file("README") == "README on master"
    assert foo_git.read_file("bar") == "bar on master"
    rc, head = foo_git.call("show", "HEAD", raises=False)
    assert rc == 0
    assert "Merge" not in head

def test_abort_if_unclean(git_server, tmpdir, test_git):
    foo_git = create_foo(git_server, tmpdir, test_git)
    branch = Branch()
    branch.name = "master"
    branch.tracks = "origin"
    git_server.push_file("foo.git", "README", "README on master")
    foo_git.sync_branch(branch)
    foo_git.root.join("README").write("changing README")
    (res, message) = foo_git.sync_branch(branch)
    assert res is False
    assert "unstaged changes" in message
