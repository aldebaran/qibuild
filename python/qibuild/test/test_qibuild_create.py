import qisrc.git

def test_simple(qibuild_action):
    foo_proj = qibuild_action("create", "foo", worktree=qibuild_action.worktree)
    qibuild_action("configure", "foo")

def test_with_git(qibuild_action):
    qibuild_action("create", "foo", "--git")
    qibuild_action.reload_worktree()
    qibuild_action("configure", "foo")
    foo_proj = qibuild_action.build_worktree.get_build_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    ret, out = git.call("show", "HEAD", raises=False)
    assert ret == 0
    assert ".gitignore" in out

