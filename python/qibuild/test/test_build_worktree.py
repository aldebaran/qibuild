def test_read_deps(build_worktree):
    build_worktree.create_project("world")
    build_worktree.create_project("hello", depends=["world"])
    hello = build_worktree.get_build_project("hello")
    assert hello.depends == set(["world"])
