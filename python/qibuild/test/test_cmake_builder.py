## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.error
import qibuild.cmake_builder
import qibuild.config
import qibuild.parsers

import mock
import pytest

from qisrc.test.conftest import git_server, qisrc_action
from qibuild.test.conftest import TestBuildWorkTree

def test_check_configure_has_been_called_before_building(build_worktree):
    hello_proj = build_worktree.create_project("hello")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [hello_proj])

    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.cmake_builder.NotConfigured):
        cmake_builder.build()

def test_default_install(build_worktree, toolchains, tmpdir):
    hello_proj = build_worktree.create_project("hello", run_depends="bar")
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
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

def test_sdk_dirs(build_worktree):
    foo_proj = build_worktree.create_project("foo")
    bar_proj = build_worktree.create_project("bar", build_depends=["foo"])
    baz_proj = build_worktree.create_project("baz", build_depends=["bar"])
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [bar_proj])
    sdk_dirs_when_top_project = cmake_builder.get_sdk_dirs_for_project(bar_proj)
    cmake_builder.projects = [baz_proj]
    sdk_dirs_when_not_top_project = cmake_builder.get_sdk_dirs_for_project(bar_proj)
    assert sdk_dirs_when_top_project == sdk_dirs_when_not_top_project

def test_add_package_paths_from_toolchain(build_worktree, toolchains, monkeypatch):
    toolchains.create("test")
    qibuild.config.add_build_config("test", toolchain="test")
    boost_package = toolchains.add_package("test", "boost")
    pthread_package = toolchains.add_package("test", "pthread")
    qi_package = toolchains.add_package("test", "libqi", build_depends=["boost"])
    naoqi_proj = build_worktree.create_project("naoqi", build_depends=["libqi"])
    build_worktree.set_active_config("test")
    os.environ["QIBUILD_LOOSE_DEPS_RESOLUTION"] = "ON"
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [naoqi_proj])
    sdk_dirs = cmake_builder.get_sdk_dirs_for_project(naoqi_proj)
    assert sdk_dirs == [boost_package.path, qi_package.path, pthread_package.path]
    del os.environ["QIBUILD_LOOSE_DEPS_RESOLUTION"]
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [naoqi_proj])
    sdk_dirs = cmake_builder.get_sdk_dirs_for_project(naoqi_proj)
    assert sdk_dirs == [boost_package.path, qi_package.path]

def test_host_tools_happy_path(build_worktree, fake_ctc):
    footool = build_worktree.add_test_project("footool")
    footool.configure()
    host_sdk_dir = footool.sdk_directory
    usefootool_proj = build_worktree.add_test_project("usefootool")
    build_worktree.set_active_config("fake-ctc")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    host_dirs = cmake_builder.get_host_dirs(usefootool_proj)
    assert host_dirs == [host_sdk_dir]

def test_host_tools_no_host_config(build_worktree, fake_ctc):
    footool = build_worktree.add_test_project("footool")
    usefootool_proj = build_worktree.add_test_project("usefootool")
    build_worktree.set_active_config("fake-ctc")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    # pylint:disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        cmake_builder.get_host_dirs(usefootool_proj)
    assert "`qibuild set-host-config`" in e.value.message

def test_host_tools_host_tools_not_built(build_worktree, fake_ctc):
    qibuild.config.add_build_config("foo", host=True)
    footool = build_worktree.add_test_project("footool")
    usefootool_proj = build_worktree.add_test_project("usefootool")
    build_worktree.set_active_config("fake-ctc")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    # pylint:disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        cmake_builder.get_host_dirs(usefootool_proj)
    assert "(Using 'foo' build config)" in e.value.message

def test_setting_loose_deps_resolution_from_manifest(git_server, qisrc_action):
    git_server.set_loose_deps_resolution()
    qisrc_action("init", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    assert cmake_builder.loose_deps_resolution == True
