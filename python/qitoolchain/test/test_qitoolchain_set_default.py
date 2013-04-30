import qibuild.test.conftest

def test_simple(qitoolchain_action, tmpdir):
    qitoolchain_action("create", "foo")
    build_worktree = qibuild.test.conftest.TestBuildWorkTree(tmpdir.strpath)
    qitoolchain_action.chdir(tmpdir.strpath)
    qitoolchain_action("set-default", "foo")
