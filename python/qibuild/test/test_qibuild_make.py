## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import time
import subprocess

import qisys.command
import qibuild.build
import qibuild.cmake_builder
import qibuild.find
import qitoolchain.qipackage

from qisys.test.conftest import skip_on_win

import pytest

def test_running_from_build_dir(qibuild_action):
    # Running `qibuild configure hello` `qibuild make hello` and running
    # the `hello` executable should work out of the box

    qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    hello = qibuild.find.find_bin([hello_proj.sdk_directory], "hello")
    qisys.command.call([hello])

def test_make_without_configure(qibuild_action):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.cmake_builder.NotConfigured):
        qibuild_action("make", "-s", "hello")

def test_running_from_build_dir_incremental(qibuild_action):
    qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("make", "hello")
    hello = qibuild.find.find_bin([hello_proj.sdk_directory], "hello")
    qisys.command.call([hello])

@skip_on_win
def test_using_host_tools_for_cross_compilation_no_system(qibuild_action, fake_ctc):
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    qibuild_action("configure", "footool")
    qibuild_action("make", "footool")
    qibuild_action("configure", "usefootool", "--config", "fake-ctc")
    qibuild_action("make", "usefootool", "--config", "fake-ctc")

@skip_on_win
def test_using_host_tools_for_cross_compilation_with_host_config(qibuild_action, fake_ctc):
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    qibuild_action("add-config", "foo")
    qibuild_action("set-host-config", "foo")
    qibuild_action("configure", "footool", "--config", "foo")
    qibuild_action("make", "footool", "--config", "foo")
    qibuild_action("configure", "usefootool", "--config", "fake-ctc")
    qibuild_action("make", "usefootool", "--config", "fake-ctc")

@skip_on_win
def test_using_host_tools_for_cross_with_host_in_toolchain(qibuild_action,
                                                           qitoolchain_action,
                                                           fake_ctc):
    footool_proj = qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    footool_archive = qibuild_action("package", "footool")
    qitoolchain_action("add-package", "-c", "fake-ctc", footool_archive)
    qisys.sh.rm(footool_proj.path)
    qibuild_action("configure", "usefootool", "--config", "fake-ctc")
    qibuild_action("make", "usefootool", "--config", "fake-ctc")

def test_parallel_build(qibuild_action):
    qibuild_action.create_project("a")
    qibuild_action.create_project("b")
    qibuild_action.create_project("c", build_depends=["a", "b"])
    qibuild_action("configure", "c")
    qibuild_action("make", "c", "--num-workers=2")

def test_codegen_happy(qibuild_action):
    qibuild_action.add_test_project("codegen")
    qibuild_action("configure", "codegen")
    qibuild_action("make", "codegen", "--verbose-make")

def test_codegen_fail_when_generating_command_fails(qibuild_action):
    qibuild_action.add_test_project("codegen")
    qibuild_action("configure", "codegen", "-DFAIL=TRUE")
    # Bug in pytest, with pytest.raises() pytest fails with:
    # ExceptionInfo object has no attribute 'typename'
    # (but only when used with the xdist plugin on Windows)
    try:
        qibuild_action("make", "codegen", "--verbose-make")
        # pylint:disable-msg=E1101
        pytest.fail("Build should have fail")
    except qibuild.build.BuildFailed:
        pass

def test_depend_on_the_generator_command(qibuild_action):
    project = qibuild_action.add_test_project("codegen")
    gen_py = os.path.join(project.path, "gen.py")
    qibuild_action("configure", "codegen")
    qibuild_action("make", "codegen", "--verbose-make")
    with open(gen_py, "r") as fp:
        lines = fp.readlines()
    lines.append("sys.exit('Kaboom!')\n")
    with open(gen_py, "w") as fp:
        fp.writelines(lines)
    # Make sure mtime of the gen.py script is recent
    # Make sure that re-running make cause re-running the generator
    # command and thus fail the build
    now = time.time()
    os.utime(gen_py, (now + 10, now + 10))
    # See above for why we do not use with pytest.raise()
    try:
        qibuild_action("make", "codegen")
        # pylint: disable-msg=E1101
        pytest.fail("Build should have fail!")
    except qibuild.build.BuildFailed:
        pass
