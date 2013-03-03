import qisys.sh
import qisys.script
import qisys.worktree

def test_qisrc_remove_exsiting(qisrc_action):
    worktree = qisrc_action.worktree
    foo_proj = worktree.create_project("foo")
    qisrc_action("remove", "foo")
    worktree = qisrc_action.worktree
    assert not worktree.get_project("foo")
    assert worktree.tmpdir.join("foo").check(dir=True)

def test_qisrc_remove_existing_from_disk(qisrc_action):
    worktree = qisrc_action.worktree
    worktree.create_project("foo")
    qisrc_action("remove", "foo", "--from-disk")
    worktree = qisrc_action.worktree
    assert not worktree.get_project("foo")
    assert not worktree.tmpdir.join("foo").check(dir=True)

def test_qisrc_fails_when_not_exists(qisrc_action):
    qisrc_action("init")
    error = qisrc_action("remove", "foo", raises=True)
    assert "No such project: foo" in error
