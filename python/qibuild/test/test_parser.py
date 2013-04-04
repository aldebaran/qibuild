import qibuild.parsers

def test_parse_one_arg(build_worktree, args):
    world = build_worktree.create_project("world")

    args.projects = ["world"]
    projects = qibuild.parsers.get_build_projects(build_worktree, args)
    assert projects == [world]

def test_set_generator(build_worktree, args):
    args.cmake_generator = "Ninja"
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    assert build_config.cmake_generator == "Ninja"
