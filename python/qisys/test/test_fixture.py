import pytest

def test_worktree(tmpdir, worktree):
    assert worktree.root == str(tmpdir.join("work"))
    assert len(worktree.projects) == 0
    assert len(worktree.buildable_projects) == 0
    assert tmpdir.join("work").join(".qi").join("worktree.xml").check(file=1)

