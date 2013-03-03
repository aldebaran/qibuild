
def test_qisrc_foreach(tmpdir, monkeypatch):
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    foo = tmpdir.mkdir("foo")
    worktree.add_project("foo")
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qisrc.actions.foreach", ["foo"])
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    assert not worktree.get_project("foo")
    assert foo.check(dir=True)
