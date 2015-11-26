## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.qixml
import qisrc.git
import qibuild.config

import pytest

def test_dependencies_cmake(build_worktree):
    hello_proj = build_worktree.create_project("hello")
    hello_proj.write_dependencies_cmake(list())
    dep_cmake = os.path.join(hello_proj.build_directory,
                             "dependencies.cmake")
    # only way to check this really works is to build some
    # cmake projects, so no other assertions here
    assert os.path.exists(dep_cmake)

def test_parse_num_jobs_happy_path(build_worktree):
    hello = build_worktree.create_project("hello")
    assert hello.parse_num_jobs(3, cmake_generator="Unix Makefiles") ==  ["-j", "3"]
    assert hello.parse_num_jobs(2, cmake_generator="Ninja") ==  ["-j", "2"]
    # Don't force -j1 when using Ninja
    assert hello.parse_num_jobs(None, cmake_generator="Ninja") == list()
    assert hello.parse_num_jobs(1, cmake_generator="Ninja") ==  ["-j", "1"]

def test_parse_num_jobs_unsupported_generator(build_worktree):
    hello = build_worktree.create_project("hello")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        hello.parse_num_jobs(3, cmake_generator="NMake Makefiles") ==  list()
    assert "-j is not supported for NMake Makefiles" in str(e.value)

def test_parse_num_jobs_no_dash_j(build_worktree, record_messages):
    hello = build_worktree.create_project("hello")
    assert hello.parse_num_jobs(3, cmake_generator="Visual Studio 10") == ["/maxcpucount:3"]

def test_parse_num_jobs_unknown_generator(build_worktree, record_messages):
    hello = build_worktree.create_project("hello")
    assert hello.parse_num_jobs(3, cmake_generator="KDevelop3") ==  list()
    assert record_messages.find("Unknown generator: KDevelop3")

def test_gen_scm_info(build_worktree, tmpdir):
    build_worktree.add_test_project("world")
    hello_proj = build_worktree.add_test_project("hello")
    git = qisrc.git.Git(hello_proj.path)
    git.init()
    git.add(".")
    git.commit("--message", "initial commit")
    rc, sha1 = git.call("rev-parse", "HEAD", raises=False)
    package_xml = tmpdir.join("package.xml").strpath
    hello_proj.gen_package_xml(package_xml)
    tree = qisys.qixml.read(package_xml)
    scm_elem = tree.find("scm")
    git_elem = scm_elem.find("git")
    assert git_elem.get("revision") == sha1

def test_using_build_prefix(build_worktree):
    world_proj = build_worktree.add_test_project("world")
    build_config = build_worktree.build_config
    build_config.build_prefix = "mybuild"
    build_directory_name = build_config.build_directory()
    assert world_proj.build_directory == os.path.join(build_worktree.root, "mybuild",
                                                      build_directory_name, "world")

def test_validates_name(build_worktree):
    # pylint:disable-msg=E1101
    with pytest.raises(Exception):
        build_worktree.create_project("foo/bar")

def test_get_host_sdk_dir_no_system(build_worktree, toolchains, fake_ctc):
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    qibuild_cfg.set_host_config("foo")
    qibuild_cfg.write()
    assert qibuild_cfg.get_host_config() == "foo"
    bar_proj = build_worktree.create_project("bar")
    build_worktree.set_active_config("foo")
    host_sdk_dir = bar_proj.sdk_directory
    build_worktree.set_active_config("fake-ctc")
    assert bar_proj.get_host_sdk_dir() == host_sdk_dir

def test_get_host_sdk_dir_system(build_worktree, toolchains, fake_ctc):
    bar_proj = build_worktree.create_project("bar")
    system_sdk_dir = bar_proj.sdk_directory
    build_worktree.set_active_config("fake-ctc")
    assert bar_proj.get_host_sdk_dir() == system_sdk_dir
