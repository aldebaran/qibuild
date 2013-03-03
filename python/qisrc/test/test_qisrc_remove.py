import qisys.sh
import qisys.script
import qisys.worktree

def test_qisrc_rm(tmpdir, monkeypatch):
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    foo = tmpdir.mkdir("foo")
    worktree.add_project("foo")
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qisrc.actions.remove", ["foo"])
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    assert not worktree.get_project("foo")
    assert foo.check(dir=True)

def test_qisrc_rm_from_disk(tmpdir, monkeypatch):
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    foo = tmpdir.mkdir("foo")
    worktree.add_project("foo")
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qisrc.actions.remove", ["foo", "--from-disk"])
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    assert not worktree.get_project("foo")
    assert not foo.check(dir=True)
