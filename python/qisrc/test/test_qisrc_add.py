import qisys.sh
import qisys.script
import qisys.worktree
import qisrc.worktree


import pytest

def test_qisrc_add_dot(qisrc_action):
    worktree = qisrc_action.worktree
    tmpdir = qisrc_action.tmpdir
    foo = tmpdir.mkdir("foo")
    qisrc_action("add", ".", cwd=foo)
    worktree = qisrc_action.worktree
    assert worktree.get_project("foo")

def test_qisrc_add_url(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    foo.remote_url = "file://" + foo.remote_url
    qisrc_action("init")
    qisrc_action("add", foo.remote_url)
    assert qisrc_action.git_worktree.get_git_project("foo")

def test_qisrc_add_url_in_subdir(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    foo.remote_url = "file://" + foo.remote_url
    qisrc_action("init")
    lib = qisrc_action.tmpdir.mkdir("lib")
    qisrc_action("add", foo.remote_url, cwd=lib)
    assert qisrc_action.git_worktree.get_git_project("lib/foo")

def test_qisrc_add_already_exists(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    foo.remote_url = "file://" + foo.remote_url
    qisrc_action("init")
    qisrc_action.tmpdir.mkdir("foo")
    error = qisrc_action("add", foo.remote_url, raises=True)
    assert "already exists" in error
