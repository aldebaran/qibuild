#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Configure """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import platform
import subprocess
import pytest

import qisrc.git
import qitoolchain
import qisys.command
import qibuild.find
import qibuild.cmake
import qibuild.config
from qibuild.test.conftest import TestBuildWorkTree
from qipy.test.conftest import qipy_action


def test_simple(qibuild_action):
    """ Test Simple """""
    # Just make sure that the basic stuff works (find qibuild-config.cmake)
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")


def test_deps(qibuild_action):
    """ Test Deps """
    # Running `qibuild configure hello` should work out of the box
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    # As should `qibuild configure --all`
    qibuild_action("configure", "-a")


def test_single(qibuild_action, record_messages):
    """ Test Single """
    # We need to configure world at least once before testing anything
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    # Now make sure `qibuild configure -s` works:
    record_messages.reset()
    qibuild_action("configure", "hello", "--single")
    assert not record_messages.find("world")


def test_qi_use_lib(qibuild_action):
    """ Test Qi Use Lib """
    use_lib_proj = qibuild_action.add_test_project("uselib")
    qibuild_action("configure", "uselib")
    # Read cache and check that DEPENDS value are here
    cmake_cache = use_lib_proj.cmake_cache
    cache = qibuild.cmake.read_cmake_cache(cmake_cache)
    assert cache["D_DEPENDS"] == "A;B"
    assert cache["E_DEPENDS"] == "D;A;B;CC"
    # Make sure it builds
    qibuild_action("make", "uselib")
    # Make sure it fails when it should
    with pytest.raises(Exception):
        qibuild_action("configure", "uselib", "-DSHOULD_FAIL=ON")


def test_qi_stage_lib_simple(qibuild_action):
    """ Test Qi Stage Lib Simple """
    qibuild_action.add_test_project("stagelib")
    qibuild_action("configure", "stagelib")


def test_qi_stage_lib_but_really_bin(qibuild_action):
    """ Test Qi Stage Lib But Really Bin """
    qibuild_action.add_test_project("stagelib")
    with pytest.raises(qibuild.build.ConfigureFailed):
        qibuild_action("configure", "stagelib",
                       "-DSHOULD_FAIL_STAGE_LIB_BUT_REALLY_BIN=ON")


def test_qi_stage_lib_but_no_such_target(qibuild_action):
    """ Test Qi Stage Lib But No Such Target """
    qibuild_action.add_test_project("stagelib")
    with pytest.raises(Exception):
        qibuild_action("configure", "stagelib",
                       "-DSHOULD_FAIL_STAGE_NO_SUCH_TARGET")


def test_preserve_cache(qibuild_action):
    """ Test Preserve Cache """
    foo_proj = qibuild_action.add_test_project("foo")
    qibuild_action("configure", "foo")
    # Read cache and check that DEPENDS value are here
    cache_before = qibuild.cmake.read_cmake_cache(foo_proj.cmake_cache)
    assert cache_before["EGGS_DEPENDS"] == "SPAM"
    assert cache_before["BAR_DEPENDS"] == "EGGS;SPAM"
    # run cmake .. and check the cache did not change
    qisys.command.call(["cmake", ".."], cwd=foo_proj.build_directory)
    cache_after = qibuild.cmake.read_cmake_cache(foo_proj.cmake_cache)
    if os.name == 'nt':
        # no way to prevent CMake from storing c:\Users in the cache ...
        for k in cache_before:
            cache_before[k] = cache_before[k].lower()
        for k in cache_after:
            cache_after[k] = cache_after[k].lower()
    assert cache_before == cache_after


def test_config_h_simple(qibuild_action, tmpdir):
    """ Test Config h Simple """
    _proj = qibuild_action.add_test_project("config_h")
    qibuild_action("configure", "config_h")
    qibuild_action("make", "config_h")
    qibuild_action("install", "config_h", tmpdir.strpath)
    foo1 = qibuild.find.find_bin([tmpdir.strpath], "foo")
    process = subprocess.Popen([foo1])
    process.wait()
    assert process.returncode == 42
    assert tmpdir.join("include", "foo", "config.h").check(file=1)


@pytest.mark.xfail
def test_config_h_extra_install_rule(qibuild_action, tmpdir):
    """ Test Config h Extra Install Rule """
    proj = qibuild_action.add_test_project("config_h")
    qibuild_action("configure", "config_h", "-DWITH_EXTRA_INSTALL_RULE=ON")
    qibuild_action("make", "config_h")
    qibuild_action("install", "config_h", tmpdir.strpath)
    full_config_h = os.path.join(proj.build_directory,
                                 "include", "foo", "config.h")
    full_config_h = os.path.join(tmpdir.strpath, full_config_h)
    assert not os.path.exists(full_config_h)


def test_detects_incorrect_cmake(qibuild_action):
    """ Test Detect Incorrect CMake """
    _proj = qibuild_action.add_test_project("incorrect_cmake")
    qibuild_action("configure", "incorrect_cmake", raises=True)


def test_git_version(qibuild_action):
    """ Test Git Version """
    proj = qibuild_action.add_test_project("gitversion")
    git = qisrc.git.Git(proj.path)
    git.call("init")
    git.call("add", ".")
    git.call("commit", "--message", "initial commit")
    git.call("tag", "v0.1")
    qibuild_action("configure", "gitversion")
    qibuild_action("make", "gitversion")
    testversion = qibuild.find.find_bin([proj.sdk_directory], "testversion")
    process = subprocess.Popen(testversion, stdout=subprocess.PIPE)
    out, _ = process.communicate()
    assert out.strip() == "v0.1"


def test_submodule(qibuild_action):
    """ Test SubModule """
    qibuild_action.add_test_project("submodule")
    qibuild_action("configure", "submodule")
    qibuild_action("make", "submodule")


def test_pycmd(qibuild_action):
    """ Test PyCmd """
    pycmd_proj = qibuild_action.add_test_project("pycmd")
    pycmd_proj.configure()
    test_txt = os.path.join(pycmd_proj.build_directory, "test.txt")
    with open(test_txt, "r") as fp:
        assert fp.read() == "Written from Python\n"
    qibuild_action("configure", "pycmd", "-DFAIL=TRUE", raises=True)


def test_cmake_option_build_test_on(qibuild_action):
    """ Test CMake Option Build Test On """
    project = qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme", "-DQI_WITH_TESTS=ON")
    qibuild_action("make", "testme")
    project.build()
    test_path = qibuild.find.find([project.sdk_directory], "ok")
    assert test_path is not None
    assert os.path.exists(test_path)


def test_cmake_option_build_test_off(qibuild_action):
    """ Test CMake Option Build Test Off """
    project = qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme", "-DQI_WITH_TESTS=OFF")
    qibuild_action("make", "testme")
    test_path = qibuild.find.find([project.sdk_directory], "ok", expect_one=False)
    assert not test_path


def test_cmake_option_build_perf_test_on(qibuild_action):
    """ Test CMake Option Build Perf Test On """
    project = qibuild_action.add_test_project("perf")
    qibuild_action("configure", "perf", "-DQI_WITH_PERF_TESTS=ON")
    qibuild_action("make", "perf")
    project.build()
    test_path = qibuild.find.find([project.sdk_directory], "perf_spam")
    assert test_path is not None
    assert os.path.exists(test_path)


def test_cmake_option_build_perf_test_off(qibuild_action):
    """ Test CMake Option Build Perf Test Off """
    project = qibuild_action.add_test_project("perf")
    qibuild_action("configure", "perf", "-DQI_WITH_PERF_TESTS=OFF")
    qibuild_action("make", "perf")
    test_path = qibuild.find.find([project.sdk_directory], "perf_spam", expect_one=False)
    assert not test_path


def read_path_conf(project):
    """ Read Path Conf """
    path_conf_path = os.path.join(project.sdk_directory,
                                  "share", "qi", "path.conf")
    with open(path_conf_path, "r") as fp:
        return fp.read()


def test_using_dash_s_with_path_conf(qibuild_action):
    """ Test Using Dash s With Path Conf """
    stagepath_proj = qibuild_action.add_test_project("stagepath")
    _usepath_proj = qibuild_action.add_test_project("usepath")
    qibuild_action("configure", "usepath")
    path_conf_before = read_path_conf(stagepath_proj)
    qibuild_action("configure", "-s", "usepath")
    path_conf_after = read_path_conf(stagepath_proj)
    assert path_conf_before == path_conf_after


def test_staged_path_first_in_path_conf(qibuild_action, toolchains):
    """ Test Staged Path First In Path Conf """
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    bar_package = toolchains.add_package("foo", "bar")
    qibuild_action.add_test_project("stagepath")
    qibuild_action("configure", "stagepath", "--config", "foo")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("foo")
    stagepath_proj = build_worktree.get_build_project("stagepath")
    path_conf = read_path_conf(stagepath_proj)
    lines = path_conf.splitlines()
    assert lines == [
        stagepath_proj.path,
        stagepath_proj.sdk_directory,
        bar_package.path
    ]


def test_path_conf_contains_toolchain_paths(qibuild_action, toolchains):
    """ Test PAth Conf Contais Toolchain Paths """
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    toolchains.add_package("foo", "bar")
    foo_tc = qitoolchain.get_toolchain("foo")
    bar_path = foo_tc.get_package("bar").path
    qibuild_action.add_test_project("hello")
    qibuild_action.add_test_project("world")
    build_woktree = TestBuildWorkTree()
    build_woktree.build_config.set_active_config("foo")
    qibuild_action("configure", "hello", "--config", "foo")
    world_proj = build_woktree.get_build_project("world")
    hello_proj = build_woktree.get_build_project("hello")
    path_conf = os.path.join(hello_proj.sdk_directory, "share", "qi", "path.conf")
    with open(path_conf, "r") as fp:
        contents = fp.readlines()
    sdk_dirs = [x.strip() for x in contents]
    assert hello_proj.sdk_directory in sdk_dirs
    assert world_proj.sdk_directory in sdk_dirs
    assert bar_path in sdk_dirs


def test_adding_a_new_test(qibuild_action):
    """ Test Adding a New Test """
    qibuild_proj = qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    test_proj1 = qibuild_proj.to_test_project()
    num_tests_before = len(test_proj1.tests)
    cmake_lists = os.path.join(qibuild_proj.path, "CMakeLists.txt")
    with open(cmake_lists, "a") as fp:
        fp.write("""\nqi_create_test(env2 env.cpp)\n""")
    qibuild_action("make", "testme")
    test_proj2 = qibuild_proj.to_test_project()
    num_tests_after = len(test_proj2.tests)
    assert num_tests_after == num_tests_before + 1


def test_using_build_prefix_from_command_line(qibuild_action, tmpdir):
    """ Test Using Build Prefix From Command Line """
    qibuild_action.add_test_project("world")
    prefix = tmpdir.join("mybuild")
    qibuild_action("configure", "world", "--build-prefix", prefix.strpath)
    expected = prefix.join("build-sys-%s-%s" % (platform.system().lower(),
                                                platform.machine().lower()),
                           "world")
    assert expected.join("CMakeCache.txt").check(file=True)


def test_using_build_prefix_from_config(qibuild_action, tmpdir):
    """ Test Using Build Prefix From Config """
    build_worktree = TestBuildWorkTree()
    qibuild_action.add_test_project("world")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.local.build.prefix = "prefix"
    qibuild_cfg.write_local_config(build_worktree.qibuild_xml)
    qibuild_action("configure", "world")
    prefix = build_worktree.tmpdir.join("prefix")
    expected = prefix.join("build-sys-%s-%s" % (platform.system().lower(),
                                                platform.machine().lower()),
                           "world")
    assert expected.join("CMakeCache.txt").check(file=True)


def test_relwithdebinfo(qibuild_action):
    """ Test Rel With Deb Info """
    world_proj = qibuild_action.add_test_project("world")
    qibuild_action("configure", "world", "--build-type", "RelWithDebInfo")
    cmake_build_type = qibuild.cmake.get_cached_var(world_proj.build_directory,
                                                    "CMAKE_BUILD_TYPE")
    assert cmake_build_type == "RelWithDebInfo"


def test_using_fake_ctc(qibuild_action, fake_ctc):
    """ Test Using Fake Cross Toolchain """
    qibuild_action.add_test_project("footool")
    qibuild_action("configure", "footool", "--config", "fake-ctc")
    qibuild_action("make", "footool", "--config", "fake-ctc")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("fake-ctc")
    footool_proj = build_worktree.get_build_project("footool")
    # assert that bin/footool exists but cannot be run:
    footool = qibuild.find.find_bin([footool_proj.sdk_directory], "footool",
                                    expect_one=True)
    assert os.path.exists(footool)
    with pytest.raises(Exception):
        qisys.command.call([footool])


def test_bin_sdk(qibuild_action):
    """ Test Bin SDK """
    qibuild_action.add_test_project("binsdk")
    qibuild_action.add_test_project("binsdkuser")
    qibuild_action("configure", "binsdkuser")


def test_gtest(qibuild_action, tmpdir):
    """ Test gtest """
    qibuild_action.add_test_project("fakegtest")
    qibuild_action.add_test_project("gtestuser")
    qibuild_action("configure", "gtestuser")
    qibuild_action("make", "gtestuser")
    qibuild_action("install", "gtestuser", tmpdir.strpath)
    assert not tmpdir.join("include", "fakegtest", "gtest.h").check(file=True)


def test_setting_cflags(qibuild_action):
    """ Test Setting C Flags """
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world", "-DCMAKE_CXX_FLAGS=-std=gnu++11")


def test_virtualenv_path(qipy_action, qibuild_action):
    """ Test VirtualEnv Path """
    py_proj = qibuild_action.add_test_project("py")
    qibuild_action("configure", "py")
    qibuild_action("make", "py")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    py_test = os.path.join(py_proj.sdk_directory, "bin", "py_test")
    output = subprocess.check_output([py_test]).strip()
    bin_python = os.path.join(output, "bin", "python")
    assert os.path.exists(bin_python)
