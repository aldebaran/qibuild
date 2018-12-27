#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Testing DependenciesSolver class """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.config
from qibuild.deps import DepsSolver


def test_simple_deps(build_worktree):
    """ Test Simple Deps """
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([world], ["build"]) == [world]
    assert deps_solver.get_dep_projects([hello], ["build"]) == [world, hello]


def test_ignore_missing_deps(build_worktree):
    """ Test Ignore Missing Deps """
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world", "foo"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([hello], ["build"]) == [world, hello]


def test_runtime_deps(build_worktree):
    """ Test Runtime Deps """
    libworld = build_worktree.create_project("libworld")
    hello_plugin = build_worktree.create_project("hello-plugin")
    hello = build_worktree.create_project("hello", build_depends=["libworld"],
                                          run_depends=["hello-plugin"])
    deps_solver = DepsSolver(build_worktree)
    dep_projects = deps_solver.get_dep_projects([hello], ["build", "runtime"])
    assert dep_projects == [hello_plugin, libworld, hello]


def test_find_packages_in_toolchain(build_worktree, toolchains):
    """ Test Find Package In Toolchain """
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    world_package = toolchains.add_package("foo", "world")
    hello = build_worktree.create_project("hello", build_depends=["world"])
    build_worktree.set_active_config("foo")
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_packages([hello], ["build"]) == [world_package]


def test_prefer_sources_over_packages(build_worktree, toolchains):
    """ Test Prefer Sources Over Packages """
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    _world_package = toolchains.add_package("foo", "world")
    world_proj = build_worktree.create_project("world")
    hello_proj = build_worktree.create_project("hello", build_depends=["world"])
    build_worktree.set_active_config("foo")
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([hello_proj], ["build"]) == [world_proj, hello_proj]
    assert not deps_solver.get_dep_packages([hello_proj], ["build"])


def test_complex_dep_solving1(build_worktree, toolchains):
    """ Tst Complex Dep Solving """
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    _libqi_package = toolchains.add_package("foo", "libqi")
    hal_package = toolchains.add_package("foo", "hal", run_depends=["libqi"])
    _naoqi_package = toolchains.add_package("foo", "naoqi", run_depends=["hal"])
    build_worktree.create_project("libqi")
    naoqi_proj = build_worktree.create_project("naoqi", run_depends=["hal"])
    deps_solver = DepsSolver(build_worktree)
    build_worktree.set_active_config("foo")
    assert deps_solver.get_dep_packages([naoqi_proj], ["runtime"]) == \
        [hal_package]


def test_complex_dep_solving2(build_worktree, toolchains):
    """ Test Complex Dep Solving 2 """
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    behavior_proj = build_worktree.create_project("behavior", build_depends=["libqiproject"])
    toolchains.add_package("foo", "libqiproject", build_depends=["libqipackage"])
    qipackage_proj = build_worktree.create_project("libqipackage")
    deps_solver = DepsSolver(build_worktree)
    build_worktree.set_active_config("foo")
    assert deps_solver.get_dep_projects([behavior_proj], ["build"]) == \
        [qipackage_proj, behavior_proj]


def test_compute_sdk_dirs(build_worktree):
    """ Test Compute SDK Dirs """
    libworld = build_worktree.create_project("libworld")
    hello_plugin = build_worktree.create_project("hello-plugin")
    hello = build_worktree.create_project("hello", build_depends=["libworld"],
                                          run_depends=["hello-plugin"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_sdk_dirs(hello, ["build"]) == [libworld.sdk_directory]
    assert deps_solver.get_sdk_dirs(hello, ["build", "runtime"]) == \
        [hello_plugin.sdk_directory, libworld.sdk_directory]


def test_recurse_deps(build_worktree):
    """ Test Recurse Deps """
    gtest = build_worktree.create_project("gtest")
    libfoo = build_worktree.create_project("libfoo", build_depends=["gtest"])
    bar1 = build_worktree.create_project("bar", build_depends=["libfoo"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([bar1], ["build", "runtime"]) == [gtest, libfoo, bar1]


def test_empty_dep_is_single(build_worktree):
    """ Test Empty Dep Is Single """
    build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world", "foo"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([hello], list()) == [hello]


def test_simple_reverse_deps(build_worktree):
    """ Test Simple Reverse Deps """
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([world], ["build"], reverse=True) == [hello]
    assert deps_solver.get_dep_projects([hello], ["build"], reverse=True) == []


def test_complex_reverse_deps(build_worktree):
    """ Test Complex Reverse Deps """
    libworld = build_worktree.create_project("libworld")
    libhello = build_worktree.create_project("libhello", build_depends=["libworld"])
    hello_plugin = build_worktree.create_project("hello-plugin")
    hello = build_worktree.create_project("hello",
                                          build_depends=["libworld", "libhello"], run_depends=["hello-plugin"])
    top_world = build_worktree.create_project("top_world", run_depends=["hello"])
    deps_solver = DepsSolver(build_worktree)
    assert deps_solver.get_dep_projects([top_world], ["build"], reverse=True) == []
    assert deps_solver.get_dep_projects([hello], ["build"], reverse=True) == []
    assert deps_solver.get_dep_projects([hello], ["build", "runtime"], reverse=True) == [top_world]
    assert deps_solver.get_dep_projects([hello_plugin], ["runtime"], reverse=True) == [hello]
    assert deps_solver.get_dep_projects([libworld], ["build", "runtime"], reverse=True) == [hello, libhello]


def test_read_host_deps(build_worktree):
    """ Test Read Host Deps """
    _footool_proj = build_worktree.add_test_project("footool")
    usefootool_proj = build_worktree.add_test_project("usefootool")
    assert usefootool_proj.host_depends == {"footool"}
