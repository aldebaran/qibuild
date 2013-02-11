import pytest

# pylint: disable-msg=E1101
@pytest.fixture()
def worktree(tmpdir):
    from qisys.worktree import WorkTree
    worktree_dir = tmpdir.mkdir("work")
    return WorkTree(worktree_dir.strpath)

