def test_guess_solve_deps(build_worktree):
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", depends=["world"])

    print build_worktree.build_projects

