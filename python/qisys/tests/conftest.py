import pytest

@pytest.fixture()
def worktree(tmpdir):
    from qisys.worktree import WorkTree
    worktree_dir = tmpdir.mkdir("work")
    return WorkTree(worktree_dir.strpath)

