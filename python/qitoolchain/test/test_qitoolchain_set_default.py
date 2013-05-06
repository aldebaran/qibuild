from qibuild.test.conftest import TestBuildWorkTree

def test_simple(qitoolchain_action):
    qitoolchain_action("create", "foo")
    qitoolchain_action("set-default", "-c", "foo")
    build_worktree = TestBuildWorkTree()
    toolchain = build_worktree.toolchain
    assert toolchain
    assert toolchain.name == "foo"
