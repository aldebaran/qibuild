import os

import qitoolchain.qipackage

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_simple(qibuild_action):
    qibuild_action.add_test_project("world")
    world_archive = qibuild_action("package", "world")
    assert os.path.exists(world_archive)
    qipackage = qitoolchain.qipackage.from_archive(world_archive)
    assert qipackage.name == "world"

def test_using_toolchain(cd_to_tmpdir):
    qibuild_action = QiBuildAction()
    qitoolchain_action = QiToolchainAction()
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qitoolchain_action("add-package", "-c", "foo", world_package)
    build_worktree.worktree.remove_project("world", from_disk=True)

    # this should now fail (no world-config.cmake found)
    qibuild_action("configure", "hello", raises=True)

    # but this should pass:
    qibuild_action("configure", "-c", "foo", "hello")
