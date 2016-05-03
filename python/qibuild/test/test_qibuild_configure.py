## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import platform
import subprocess
import time

import qisys.command
import qisys.error
import qisys.sh
import qibuild.cmake
import qibuild.config
import qibuild.find
import qisrc.git
import qitoolchain

from qibuild.test.conftest import TestBuildWorkTree
from qipy.test.conftest import qipy_action

import mock
import py
import pytest

# Make sure we cannot run tests without pywin32 installed
if os.name == "nt":
    import win32api

# This module also serves as a test for the
# qibuild cmake API


def test_simple(qibuild_action):
    # Just make sure that the basic stuff works
    # (find qibuild-config.cmake)
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")

def test_deps(qibuild_action):
    # Running `qibuild configure hello` should work out of the box
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")

    # As should `qibuild configure --all`
    qibuild_action("configure", "-a")

def test_single(qibuild_action, record_messages):
    # We need to configure world at least once before testing
    # anything
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")

    # Now make sure `qibuild configure -s` works:
    record_messages.reset()
    qibuild_action("configure", "hello", "--single")
    assert not record_messages.find("world")


def test_qi_use_lib(qibuild_action):
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
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        qibuild_action("configure", "uselib", "-DSHOULD_FAIL=ON")


def test_qi_stage_lib_simple(qibuild_action):
    qibuild_action.add_test_project("stagelib")
    qibuild_action("configure", "stagelib")

def test_qi_stage_lib_but_really_bin(qibuild_action):
    qibuild_action.add_test_project("stagelib")
    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.build.ConfigureFailed):
        qibuild_action("configure", "stagelib",
                       "-DSHOULD_FAIL_STAGE_LIB_BUT_REALLY_BIN=ON")

def test_qi_stage_lib_but_no_such_target(qibuild_action):
    qibuild_action.add_test_project("stagelib")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        qibuild_action("configure", "stagelib",
                       "-DSHOULD_FAIL_STAGE_NO_SUCH_TARGET")

def test_preserve_cache(qibuild_action):
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
        # no way to prevent CMake from storing c:\Users
        # in the cache ...
        for k in cache_before:
            cache_before[k] = cache_before[k].lower()
        for k in cache_after:
            cache_after[k] = cache_after[k].lower()
    assert cache_before == cache_after

def test_config_h_simple(qibuild_action, tmpdir):
    proj = qibuild_action.add_test_project("config_h")
    qibuild_action("configure", "config_h")
    qibuild_action("make", "config_h")
    qibuild_action("install", "config_h", tmpdir.strpath)
    foo = qibuild.find.find_bin([tmpdir.strpath], "foo")
    process = subprocess.Popen([foo])

    process.wait()
    assert process.returncode == 42
    assert tmpdir.join("include", "foo", "config.h").check(file=1)

# pylint: disable-msg=E1101
@pytest.mark.xfail
def test_config_h_extra_install_rule(qibuild_action, tmpdir):
    proj = qibuild_action.add_test_project("config_h")
    qibuild_action("configure", "config_h", "-DWITH_EXTRA_INSTALL_RULE=ON")
    qibuild_action("make", "config_h")
    qibuild_action("install", "config_h", tmpdir.strpath)
    full_config_h = os.path.join(proj.build_directory,
            "include", "foo", "config.h")
    full_config_h = os.path.join(tmpdir.strpath, full_config_h)
    assert not os.path.exists(full_config_h)

def test_detects_incorrect_cmake(qibuild_action):
    proj = qibuild_action.add_test_project("incorrect_cmake")
    qibuild_action("configure", "incorrect_cmake", raises=True)

def test_git_version(qibuild_action):
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
    qibuild_action.add_test_project("submodule")
    qibuild_action("configure", "submodule")
    qibuild_action("make", "submodule")

def test_pycmd(qibuild_action):
    pycmd_proj = qibuild_action.add_test_project("pycmd")
    pycmd_proj.configure()
    test_txt = os.path.join(pycmd_proj.build_directory, "test.txt")
    with open(test_txt, "r") as fp:
        assert fp.read() == "Written from Python\n"
    qibuild_action("configure", "pycmd", "-DFAIL=TRUE", raises=True)

def test_cmake_option_build_test_on(qibuild_action):
    project = qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme", "-DQI_WITH_TESTS=ON")
    qibuild_action("make", "testme")
    project.build()
    test_path = qibuild.find.find([project.sdk_directory], "ok")
    assert test_path is not None
    assert os.path.exists(test_path)

def test_cmake_option_build_test_off(qibuild_action):
    project = qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme", "-DQI_WITH_TESTS=OFF")
    qibuild_action("make", "testme")
    test_path = qibuild.find.find([project.sdk_directory], "ok", expect_one=False)
    assert not test_path

def test_cmake_option_build_perf_test_on(qibuild_action):
    project = qibuild_action.add_test_project("perf")
    qibuild_action("configure", "perf", "-DQI_WITH_PERF_TESTS=ON")
    qibuild_action("make", "perf")
    project.build()
    test_path = qibuild.find.find([project.sdk_directory], "perf_spam")
    assert test_path is not None
    assert os.path.exists(test_path)

def test_cmake_option_build_perf_test_off(qibuild_action):
    project = qibuild_action.add_test_project("perf")
    qibuild_action("configure", "perf", "-DQI_WITH_PERF_TESTS=OFF")
    qibuild_action("make", "perf")
    test_path = qibuild.find.find([project.sdk_directory], "perf_spam", expect_one=False)
    assert not test_path

def read_path_conf(project):
    path_conf_path = os.path.join(project.sdk_directory,
                                  "share", "qi", "path.conf")
    with open(path_conf_path, "r") as fp:
        return fp.read()

def test_using_dash_s_with_path_conf(qibuild_action):
    stagepath_proj = qibuild_action.add_test_project("stagepath")
    usepath_proj = qibuild_action.add_test_project("usepath")
    qibuild_action("configure", "usepath")
    path_conf_before = read_path_conf(stagepath_proj)
    qibuild_action("configure", "-s", "usepath")
    path_conf_after = read_path_conf(stagepath_proj)
    assert path_conf_before == path_conf_after

def test_staged_path_first_in_path_conf(tmpdir, qibuild_action, toolchains):
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
    # need to resolve symlinks
    # (the path to the sources of stagepath_proj is written by CMake, so we
    # have to do that by hand)
    lines = [os.path.realpath(x) for x in lines]
    expected = [
            stagepath_proj.path,
            stagepath_proj.sdk_directory,
            bar_package.path
    ]
    for actual_line, expected_line in zip(lines, expected):
        assert qisys.sh.samefile(actual_line, expected_line)

def test_path_conf_contains_toolchain_paths(qibuild_action, toolchains):
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
    qibuild_proj = qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    test_proj1 = qibuild_proj.to_test_project()
    num_tests_before = len(test_proj1.tests)
    cmake_lists = os.path.join(qibuild_proj.path, "CMakeLists.txt")
    with open(cmake_lists, "a") as fp:
        fp.write("""
qi_create_test(env2 env.cpp)
""")
    qibuild_action("make", "testme")
    test_proj2 = qibuild_proj.to_test_project()
    num_tests_after = len(test_proj2.tests)
    assert num_tests_after == num_tests_before + 1

def test_using_build_prefix_from_command_line(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    prefix = tmpdir.join("mybuild")
    qibuild_action("configure", "world", "--build-prefix", prefix.strpath)
    expected = prefix.join("build-sys-%s-%s" % (platform.system().lower(),
                                                platform.machine().lower()),
                           "world")
    assert expected.join("CMakeCache.txt").check(file=True)

def test_using_build_prefix_from_config(qibuild_action, tmpdir):
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
    world_proj = qibuild_action.add_test_project("world")
    qibuild_action("configure", "world", "--build-type", "RelWithDebInfo")
    cmake_build_type = qibuild.cmake.get_cached_var(world_proj.build_directory,
                                                    "CMAKE_BUILD_TYPE")
    assert cmake_build_type == "RelWithDebInfo"

# pylint: disable-msg=E1101
@pytest.mark.skipif(os.name == "nt", reason="No cross compilation on Windows yet")
def test_using_fake_ctc(qibuild_action, fake_ctc):
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
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        qisys.command.call([footool])

def test_bin_sdk(qibuild_action):
    qibuild_action.add_test_project("binsdk")
    qibuild_action.add_test_project("binsdkuser")
    qibuild_action("configure", "binsdkuser")

def test_gtest(qibuild_action, tmpdir):
    qibuild_action.add_test_project("fakegtest")
    qibuild_action.add_test_project("gtestuser")
    qibuild_action("configure", "gtestuser")
    qibuild_action("make", "gtestuser")
    qibuild_action("install", "gtestuser", tmpdir.strpath)
    assert not tmpdir.join("include", "fakegtest", "gtest.h").check(file=True)

def test_setting_cflags(qibuild_action):
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world", "-DCMAKE_CXX_FLAGS=-std=gnu++11")

def test_virtualenv_path(qipy_action, qibuild_action):
    py_proj = qibuild_action.add_test_project("py")
    qibuild_action("configure", "py")
    qibuild_action("make", "py")
    qipy_action("bootstrap")
    test_exe = qibuild.find.find_bin([py_proj.sdk_directory], "py_test")
    output = subprocess.check_output([test_exe]).strip()
    if os.name == "nt":
        bin_python = os.path.join(output, "Scripts", "Python.exe")
    else:
        bin_python = os.path.join(output, "bin", "python")
    assert os.path.exists(bin_python)

def test_skips_configure(qibuild_action, record_messages):
    world_proj = qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    with mock.patch("qisys.command.call") as mock_call:
        qibuild_action("configure", "hello")
        # hello should be rebuild because it's a top project,
        # but world should be skipped
        assert len(mock_call.call_args_list) == 1
    world_cmake = os.path.join(world_proj.path, "CMakeLists.txt")
    now = time.time()
    os.utime(world_cmake, (now + 10, now + 10))
    record_messages.reset()
    with mock.patch("qisys.command.call") as mock_call:
        qibuild_action("configure", "hello")
        assert record_messages.find("Re-running CMake because CMakeLists.txt has changed")
        assert len(mock_call.call_args_list) == 2

def test_re_run_cmake_when_flags_change(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")
    record_messages.reset()
    qibuild_action("configure", "world", "-DFOO=BAR")
    assert not record_messages.find("up to date")

def test_never_skip_top_projects(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")
    record_messages.reset()
    qibuild_action("configure", "world")
    assert not record_messages.find("skipping")

def test_running_cmake_for_the_first_time(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    record_messages.reset()
    qibuild_action("configure", "hello")
    assert not record_messages.find("CMake arguments changed")

def test_dont_write_path_conf_if_configure_skip(qibuild_action):
    stagepath_proj = qibuild_action.add_test_project("stagepath")
    qibuild_action.add_test_project("usepath")
    qibuild_action("configure", "usepath")
    path_conf_first = read_path_conf(stagepath_proj)
    qibuild_action("configure", "usepath")
    path_conf_second = read_path_conf(stagepath_proj)
    assert path_conf_first == path_conf_second

def extract_and_add(tmpdir, toolchain,  package_path):
    package = qitoolchain.qipackage.from_archive(package_path)
    dest = tmpdir.mkdir(package.name)
    qitoolchain.qipackage.extract(package_path, dest.strpath)
    package.path = dest.strpath
    toolchain.add_package(package)

def test_optional_package(qibuild_action, toolchains, tmpdir):
    spam_toolchain = toolchains.create("spam")
    qibuild.config.add_build_config("spam", toolchain="spam")

    bar_project = qibuild_action.add_test_project("optional/bar")
    foo_project = qibuild_action.add_test_project("optional/foo")
    qibuild_action.add_test_project("optional/top")
    bar_package_path = qibuild_action("package", "bar")
    foo_package_path = qibuild_action("package", "foo")

    extract_and_add(tmpdir, spam_toolchain, bar_package_path)
    extract_and_add(tmpdir, spam_toolchain, foo_package_path)
    qisys.sh.rm(bar_project.path)
    qisys.sh.rm(foo_project.path)
    qibuild_action("configure", "top", "--config", "spam", "-DWITH_FOO=ON")
    # it works if you don't set WITH_FOO ...
    #qibuild_action("configure", "top", "--config", "spam")
    qibuild_action("make", "top", "--config", "spam", "--verbose-make")
