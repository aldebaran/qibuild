import os
import qipy.parsers


def test_simple(qipy_action, args):
    qipy_action.add_test_project("a_lib")
    python_worktree = qipy.parsers.get_python_worktree(args)
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    venv_path = python_worktree.venv_path
    qipy_action("clean")
    assert os.path.exists(venv_path)
    qipy_action("clean", "--force")
    assert not os.path.exists(venv_path)
