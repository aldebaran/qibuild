import qisys.sh
import qisys.script
import qisys.worktree
import qisrc.worktree


import pytest

def test_qisrc_add_dot(tmpdir, monkeypatch):
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    foo = tmpdir.mkdir("foo")
    monkeypatch.chdir(foo)
    qisys.script.run_action("qisrc.actions.add", ["."])
    # the action used its own worktree, so re-open it:
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    assert worktree.get_project("foo")

def test_qisrc_add_url(tmpdir, git_server, monkeypatch):
    foo = git_server.create_repo("foo.git")
    foo.remote_url = "file://" + foo.remote_url
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qisrc.actions.init", [])
    qisys.script.run_action("qisrc.actions.add", [foo.remote_url])
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    git_worktree = qisrc.worktree.GitWorkTree(worktree)
    assert git_worktree.get_git_project("foo")

def test_qisrc_add_url_in_subdir(tmpdir, git_server, monkeypatch):
    foo = git_server.create_repo("foo.git")
    foo.remote_url = "file://" + foo.remote_url
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qisrc.actions.init", [])
    lib = tmpdir.mkdir("lib")
    monkeypatch.chdir(lib)
    qisys.script.run_action("qisrc.actions.add", [foo.remote_url])
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    git_worktree = qisrc.worktree.GitWorkTree(worktree)
    assert git_worktree.get_git_project("lib/foo")

def test_qisrc_add_already_exists(tmpdir, git_server, monkeypatch):
    foo = git_server.create_repo("foo.git")
    foo.remote_url = "file://" + foo.remote_url
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qisrc.actions.init", [])
    tmpdir.mkdir("foo")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.script.run_action("qisrc.actions.add", [foo.remote_url])
    assert "already exists" in e.value.message
