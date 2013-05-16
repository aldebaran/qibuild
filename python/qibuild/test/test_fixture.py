def test_add_test_project(build_worktree):
    world = build_worktree.add_test_project("world")
    assert build_worktree.get_build_project("world")
