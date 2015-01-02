## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qibuild.cmake_builder
import qibuild.parsers

import mock
import pytest

def test_check_configure_has_been_called_before_building(build_worktree):
    hello_proj = build_worktree.create_project("hello")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [hello_proj])

    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.cmake_builder.NotConfigured):
        cmake_builder.build()

def test_check_configure_called_on_runtime_deps(build_worktree):
    hello_proj = build_worktree.create_project("hello", run_depends=["bar"])
    build_worktree.create_project("bar")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree,
                                                       [hello_proj])
    # qibuild configure --single
    cmake_builder.dep_types = []
    cmake_builder.configure()
    # qibuild make
    cmake_builder.dep_types = ["build", "runtime"]
    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.cmake_builder.NotConfigured):
        cmake_builder.build()

def test_default_install(build_worktree, toolchains, tmpdir):
    hello_proj = build_worktree.create_project("hello", run_depends="bar")
    toolchains.create("foo")
    build_worktree.set_active_config("foo")
    toolchains.add_package("foo", "bar")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [hello_proj])
    cmake_builder.configure()
    cmake_builder.build()
    cmake_builder.install(tmpdir.strpath)

def test_runtime_single(build_worktree, args):
    build_worktree.create_project("hello", run_depends="bar")
    args.projects = ["hello"]
    args.runtime_only = True
    args.single = True
    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    assert cmake_builder.dep_types == []
