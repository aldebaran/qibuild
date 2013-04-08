import qisys.ui
from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_no_toolchain(qitoolchain_action, record_messages):
    qitoolchain_action("list")
    assert qisys.ui.find_message("No toolchain yet")

def test_default_toolchain(tmpdir, record_messages):
    qibuild_action = QiBuildAction(worktree_root=tmpdir.strpath)
    qitoolchain_action = QiToolchainAction(worktree_root=tmpdir.strpath)
    qitoolchain_action("create", "bar")
    qitoolchain_action("create", "foo", "--default")
    record_messages.reset()
    qitoolchain_action("list")
    assert qisys.ui.find_message(" bar")
    assert qisys.ui.find_message("* foo")
