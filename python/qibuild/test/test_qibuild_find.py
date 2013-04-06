import qisys.ui

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction


def test_find_target_in_projet(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    record_messages.reset()
    qibuild_action("find", "hello", "world")
    assert qisys.ui.find_message("WORLD_LIBRARIES")

def test_find_target_in_toolchain_package(tmpdir, monkeypatch,
                                          record_messages):
    monkeypatch.chdir(tmpdir)
    qibuild_action = QiBuildAction(worktree_root=tmpdir.strpath)
    qitoolchain_action = QiToolchainAction(worktree_root=tmpdir.strpath)
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qitoolchain_action("add-package", "-c", "foo", "world", world_package)
    build_worktree.worktree.remove_project("world", from_disk=True)

    record_messages.reset()
    # this should now fail (no world-config.cmake found)
    qibuild_action.chdir("hello")
    qibuild_action("configure", "-c", "foo")
    qibuild_action("find", "world", "-c", "foo")

    assert qisys.ui.find_message("WORLD_LIBRARIES")
