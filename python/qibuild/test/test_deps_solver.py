## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Testing DependenciesSolver class

"""



from qibuild.deps_solver import DepsSolver


def test_simple_deps(build_worktree):
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([world], ["build"]) == [world]
    assert deps_solver.get_dep_projects([hello], ["build"]) == [world, hello]

def test_ignore_missing_deps(build_worktree):
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world", "foo"])

    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([hello], ["build"]) == [world, hello]

def test_runtime_deps(build_worktree):
    libworld = build_worktree.create_project("libworld")
    hello_plugin = build_worktree.create_project("hello-plugin")
    hello = build_worktree.create_project("hello", build_depends=["libworld"],
                                                   run_depends=["hello-plugin"])
    deps_solver = DepsSolver(build_worktree)
    dep_projects = deps_solver.get_dep_projects([hello], ["build", "runtime"])
    assert dep_projects == [hello_plugin, libworld, hello]

def test_find_packages_in_toolchain(build_worktree, toolchains):
    toolchains.create("foo")
    world_package = toolchains.add_package("foo", "world")
    hello = build_worktree.create_project("hello", build_depends=["world"])
    build_worktree.set_active_config("foo")

    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_packages([hello], ["build"]) == [world_package]

def test_compute_sdk_dirs(build_worktree):
    libworld = build_worktree.create_project("libworld")
    hello_plugin = build_worktree.create_project("hello-plugin")
    hello = build_worktree.create_project("hello", build_depends=["libworld"],
                                                   run_depends=["hello-plugin"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_sdk_dirs(hello, ["build"]) == [libworld.sdk_directory]
    assert deps_solver.get_sdk_dirs(hello, ["build", "runtime"]) == \
            [hello_plugin.sdk_directory, libworld.sdk_directory]

def test_recurse_deps(build_worktree):
    gtest = build_worktree.create_project("gtest")
    libfoo = build_worktree.create_project("libfoo", build_depends=["gtest"])
    bar = build_worktree.create_project("bar", build_depends=["libfoo"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([bar], ["build", "runtime"]) == [gtest, libfoo, bar]

def test_empty_dep_is_single(build_worktree):
    build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world", "foo"])

    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([hello], list()) == [hello]

def test_simple_reverse_deps(build_worktree):
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world"])

    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([world], ["build"], reverse=True) == \
        [hello]
    assert deps_solver.get_dep_projects([hello], ["build"], reverse=True) == \
        []

def test_complex_reverse_deps(build_worktree):
    libworld = build_worktree.create_project("libworld")
    libhello = build_worktree.create_project("libhello", build_depends=["libworld"])
    hello_plugin = build_worktree.create_project("hello-plugin")
    hello = build_worktree.create_project("hello",
    build_depends=["libworld", "libhello"], run_depends=["hello-plugin"])

    top_world = build_worktree.create_project("top_world", run_depends=["hello"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([top_world], ["build"], reverse=True) \
        == []
    assert deps_solver.get_dep_projects([hello], ["build"],
        reverse=True) == []
    assert deps_solver.get_dep_projects([hello], ["build", "runtime"],
         reverse=True) == [top_world]

    assert deps_solver.get_dep_projects([hello_plugin], ["runtime"],
        reverse=True) == [hello]

    assert deps_solver.get_dep_projects([libworld], ["build", "runtime"],
        reverse=True) == [hello, libhello]
