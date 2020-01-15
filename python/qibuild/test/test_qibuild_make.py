#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Make """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

import qisys.command
import qibuild.find


def test_running_from_build_dir(qibuild_action):
    """
    Test Running From Build Dir.
    Running `qibuild configure hello` `qibuild make hello` and running
    the `hello` executable should work out of the box.
    """
    qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    hello = qibuild.find.find_bin([hello_proj.sdk_directory], "hello")
    qisys.command.call([hello])


def test_make_without_configure(qibuild_action):
    """ Test Make Without Configure """
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    with pytest.raises(qibuild.cmake_builder.NotConfigured):
        qibuild_action("make", "-s", "hello")


def test_running_from_build_dir_incremental(qibuild_action):
    """ Test Running From Build Dir Incremental """
    qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("make", "hello")
    hello = qibuild.find.find_bin([hello_proj.sdk_directory], "hello")
    qisys.command.call([hello])


def test_using_host_tools_for_cross_compilation_no_system(qibuild_action, fake_ctc):
    """ Test Using Host Tools From Cross Compilation No System """
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    qibuild_action("configure", "footool")
    qibuild_action("make", "footool")
    qibuild_action("configure", "usefootool", "--config", "fake-ctc")
    qibuild_action("make", "usefootool", "--config", "fake-ctc")


def test_using_host_tools_for_cross_compilation_with_host_config(qibuild_action, fake_ctc):
    """ Test Using Host Tools For Cross Compilation With Host Config """
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    qibuild_action("add-config", "foo")
    qibuild_action("set-host-config", "foo")
    qibuild_action("configure", "footool", "--config", "foo")
    qibuild_action("make", "footool", "--config", "foo")
    qibuild_action("configure", "usefootool", "--config", "fake-ctc")
    qibuild_action("make", "usefootool", "--config", "fake-ctc")


def test_using_host_tools_for_cross_with_host_in_toolchain(qibuild_action, qitoolchain_action, fake_ctc):
    """ Test Using Host Tools For Cross With Host In Toolchain """
    footool_proj = qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("usefootool")
    footool_archive = qibuild_action("package", "footool")
    qitoolchain_action("add-package", "-c", "fake-ctc", footool_archive)
    qisys.sh.rm(footool_proj.path)
    qibuild_action("configure", "usefootool", "--config", "fake-ctc")
    qibuild_action("make", "usefootool", "--config", "fake-ctc")


def test_parallel_build(qibuild_action):
    """ Test Parallel Build """
    qibuild_action.create_project("a")
    qibuild_action.create_project("b")
    qibuild_action.create_project("c", build_depends=["a", "b"])
    qibuild_action("configure", "c")
    qibuild_action("make", "c", "--num-workers=2")
