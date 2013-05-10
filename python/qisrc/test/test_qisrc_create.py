import qisys.script
import qisrc.git
from qisys.test.conftest import TestWorkTree

def test_simple(qisrc_action):
    qisrc_action("create", "foo")
    # cannot use qibuild_action fixture without creating recursive
    # dependencies ...
    qisys.script.run_action("qibuild.actions.configure", ["foo"])

def test_with_git(qisrc_action):
    qisrc_action("create", "foo", "--git")
    worktree = TestWorkTree()
    foo_proj = worktree.get_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    ret, out = git.call("show", "HEAD", raises=False)
    assert ret == 0
    assert ".gitignore" in out

def test_in_subdir(qisrc_action):
    qisrc_action.tmpdir.mkdir("bar")
    qisrc_action.chdir("bar")
    foo_proj = qisrc_action("create", "foo")
    assert foo_proj.src == "bar/foo"
