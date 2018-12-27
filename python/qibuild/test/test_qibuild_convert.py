#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Convert """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qibuild.test.conftest import TestBuildWorkTree


def test_no_cmake(qibuild_action, record_messages):
    """ Test No CMake """
    qibuild_action.add_test_project("convert/no_cmake")
    qibuild_action.chdir("convert/no_cmake")
    qibuild_action("convert")
    assert record_messages.find("Would create")
    assert record_messages.find("--go")
    record_messages.reset()
    qibuild_action("convert", "--go")
    qibuild_action("configure")
    qibuild_action("make")


def test_pure_cmake(qibuild_action):
    """ Test Pure CMake """
    qibuild_action.add_test_project("convert/pure_cmake")
    qibuild_action.chdir("convert/pure_cmake")
    qibuild_action("convert", "--go")
    qibuild_action("configure")


def test_qibuild2(qibuild_action, record_messages):
    """ Test QiBuild 2 """
    qibuild_action.add_test_project("convert/qibuild2")
    qibuild_action.chdir("convert/qibuild2")
    qibuild_action("configure")
    qibuild_action("convert", "--go")
    qibuild_action("configure")


def test_pure_c_project(qibuild_action, tmpdir):
    """ Test Pure C Project """
    work = tmpdir.join("work")
    foo1 = work.mkdir("foo")
    foo1.join("CMakeLists.txt").write("""\ncmake_minimum_required(VERSION 3.0)\nproject(foo C)\n""")
    qibuild_action.chdir(foo1.strpath)
    qibuild_action("convert", "--go")
    qibuild_action.chdir(work.strpath)
    build_worktree = TestBuildWorkTree()
    worktree = build_worktree.worktree
    worktree.add_project("foo")
    assert build_worktree.get_build_project("foo")
