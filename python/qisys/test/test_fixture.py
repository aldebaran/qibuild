import os

def test_worktree(worktree):
    assert len(worktree.projects) == 0
    assert os.path.exists(worktree.worktree_xml)
