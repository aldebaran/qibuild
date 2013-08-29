import pytest

import qisys.sh
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

def test_get_one_project(build_worktree, args):
    build_worktree.create_project("hello")
    world = build_worktree.create_project("world")
    args.projects = ["world"]
    assert qibuild.parsers.get_one_build_project(build_worktree, args) == world
    with qisys.sh.change_cwd(world.path):
        args.projects = None
        assert qibuild.parsers.get_one_build_project(build_worktree, args) == world
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        args.all = True
        qibuild.parsers.get_one_build_project(build_worktree, args)
    assert "one project" in str(e.value)

def test_default_all(build_worktree, args):
    world_proj = build_worktree.create_project("world")
    foo_proj   = build_worktree.create_project("foo")
    hello_proj = build_worktree.create_project("hello", build_depends=["world"])
    with qisys.sh.change_cwd(hello_proj.path):
        assert qibuild.parsers.get_build_projects(build_worktree, args) == \
                [world_proj, hello_proj]
        assert qibuild.parsers.get_build_projects(build_worktree, args,
                                                  default_all=True) == \
                [foo_proj, world_proj, hello_proj]
    # can still restrict the list of projects when default_all is True
    args.projects = ["hello"]
    assert qibuild.parsers.get_build_projects(build_worktree, args,
                                              default_all=True) == \
            [world_proj, hello_proj]
