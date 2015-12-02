## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qibuild.find

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qibuild.actions import run

import pytest
import mock

def test_run_target(qibuild_action):
    project = qibuild_action.add_test_project("testme")
    project.configure()
    project.build()

    ok_bin = qibuild.find.find_bin([project.sdk_directory], "ok", expect_one=True)

    with mock.patch("os.execve") as execve_mock:
        qibuild_action("run", "ok", "arg1")
    call_args_list = execve_mock.call_args_list
    assert len(call_args_list) == 1
    binary = call_args_list[0][0][0]
    assert binary == ok_bin
    cmd = call_args_list[0][0][1]
    assert cmd == [binary, "arg1"]

def test_using_no_exec(qibuild_action):
    project = qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qibuild_action("run", "--no-exec", "ok")
    error = qibuild_action("run", "--no-exec", "fail", raises=True)
    assert "Return code is 1" in error

def test_run_system(qibuild_action):
    with mock.patch("os.execve") as execve_mock:
        qibuild_action("run", "ls")
    call_args_list = execve_mock.call_args_list
    binary = call_args_list[0][0][0]
    assert os.path.isabs(binary)
    assert os.path.basename(binary) == "ls"

def test_corner_case(qibuild_action, tmpdir):
    project = qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    tmpdir.join("work").join("ok").ensure(dir=True)
    qibuild_action("run", "--no-exec", "ok")
