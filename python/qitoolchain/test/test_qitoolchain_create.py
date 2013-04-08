from qisys import ui
from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_simple(qitoolchain_action):
    foo_tc = qitoolchain_action("create", "foo")
    assert foo_tc.packages == list()

def test_default(tmpdir):
    qibuild_action = QiBuildAction(worktree_root=tmpdir.strpath)
    qitoolchain_action = QiToolchainAction(worktree_root=tmpdir.strpath)
    build_worktree = qibuild_action.build_worktree
    foo_tc = qitoolchain_action("create", "foo", "--default")
    assert build_worktree.default_config == "foo"
