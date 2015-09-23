## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qibuild.test.conftest import TestBuildWorkTree

def test_no_cmake(qibuild_action, record_messages):
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
    qibuild_action.add_test_project("convert/pure_cmake")
    qibuild_action.chdir("convert/pure_cmake")
    qibuild_action("convert", "--go")
    qibuild_action("configure")

def test_qibuild2(qibuild_action, record_messages):
    qibuild_action.add_test_project("convert/qibuild2")
    qibuild_action.chdir("convert/qibuild2")
    qibuild_action("configure")
    qibuild_action("convert", "--go")
    qibuild_action("configure")

def test_pure_c_project(qibuild_action, tmpdir):
    work = tmpdir.join("work")
    foo = work.mkdir("foo")
    foo.join("CMakeLists.txt").write("""
cmake_minimum_required(VERSION 3.0)
project(foo C)
""")
    qibuild_action.chdir(foo.strpath)
    qibuild_action("convert", "--go")
    qibuild_action.chdir(work.strpath)
    build_worktree = TestBuildWorkTree()
    worktree = build_worktree.worktree
    worktree.add_project("foo")
    assert build_worktree.get_build_project("foo")
