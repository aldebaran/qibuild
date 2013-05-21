def test_qisrc_add_dot(qisrc_action):
    tmpdir = qisrc_action.tmpdir
    foo = tmpdir.mkdir("foo")
    qisrc_action("add", ".", cwd=foo)
    # qisrc_action re-creates a worktree, so we have
    # to reload it to get the changes
    qisrc_action.reload_worktree()
    worktree = qisrc_action.worktree
    assert worktree.get_project("foo")

def test_qisrc_add_url_at_root(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    # Just make sure the file path does not exists
    foo_url = "file://" + foo.clone_url
    qisrc_action("add", foo_url)
    qisrc_action.reload_worktree()
    git_worktree = qisrc_action.git_worktree
    assert git_worktree.get_git_project("foo")

def test_qisrc_add_url_in_subdir(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    foo_url = "file://" + foo.clone_url
    lib = qisrc_action.tmpdir.mkdir("lib")
    qisrc_action("add", foo_url, cwd=lib)
    qisrc_action.reload_worktree()
    git_worktree = qisrc_action.git_worktree
    assert git_worktree.get_git_project("lib/foo")

def test_qisrc_add_already_exists(qisrc_action, git_server):
    foo = git_server.create_repo("foo.git")
    foo_url = "file://" + foo.clone_url
    qisrc_action.tmpdir.mkdir("foo")
    error = qisrc_action("add", foo_url, raises=True)
    assert "already exists" in error
