import qibuild.parsers

def test_parse_one_arg(build_worktree, args):
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", depends=["world"])

    args.single = True
    args.projects = ["hello"]
    projects = qibuild.parsers.get_build_projects(build_worktree, args)
    assert [p.name for p in projects] == ["hello"]

    args.single = False
    args.projects = ["hello"]
    projects = qibuild.parsers.get_build_projects(build_worktree, args)
    assert [p.name for p in projects] == ["world", "hello"]


def test_set_generator(build_worktree, args):
    args.cmake_generator = "Ninja"
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    assert build_config.cmake_generator == "Ninja"
