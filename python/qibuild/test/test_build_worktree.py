import os

def test_read_deps(build_worktree):
    build_worktree.create_project("world")
    build_worktree.create_project("hello", depends=["world"])
    hello = build_worktree.get_build_project("hello")
    assert hello.depends == set(["world"])

def test_setting_build_config_sets_projects_cmake_flags(build_worktree):
    build_worktree.create_project("world")
    build_worktree.build_config.build_type = "Release"
    world = build_worktree.get_build_project("world")
    assert world.cmake_args == ["-DCMAKE_BUILD_TYPE=Release"]

def test_setting_build_config_sets_projects_build_dir(build_worktree):
    build_worktree.create_project("world")
    build_worktree.build_config.build_type = "Release"
    world = build_worktree.get_build_project("world")
    assert "-release" in os.path.basename(world.build_directory)
