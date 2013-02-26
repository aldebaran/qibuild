import os

def test_worktree(worktree):
    assert len(worktree.projects) == 0
    assert os.path.exists(worktree.qibuild_xml)
