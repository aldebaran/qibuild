## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qibuild.config
from qibuild import find

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_find_target_in_project_cmake(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    record_messages.reset()
    qibuild_action("find", "--cmake", "hello", "world")
    assert record_messages.find("WORLD_LIBRARIES")

def test_find_target_in_toolchain_package_cmake(cd_to_tmpdir, record_messages):
    qibuild_action = QiBuildAction()
    qitoolchain_action = QiToolchainAction()
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    qitoolchain_action("add-package", "-c", "foo", world_package)
    build_worktree.worktree.remove_project("world", from_disk=True)

    record_messages.reset()
    qibuild_action.chdir("hello")
    qibuild_action("configure", "-c", "foo")
    qibuild_action("find", "--cmake", "world", "-c", "foo")

    assert record_messages.find("WORLD_LIBRARIES")

def test_find_target_in_build_dir(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")

    record_messages.reset()
    qibuild_action("find", "hello", "world")
    assert record_messages.find(find.library_name("world"))

    rc = qibuild_action("find", "hello", "libworld", retcode=True)
    assert rc == 1

def test_find_target_in_toolchain_package(cd_to_tmpdir, record_messages):
    qibuild_action = QiBuildAction()
    qitoolchain_action = QiToolchainAction()
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    qitoolchain_action("add-package", "-c", "foo", world_package)

    qibuild_action.chdir("hello")
    qibuild_action("configure", "-c", "foo")
    qibuild_action("make", "-c", "foo")

    record_messages.reset()
    qibuild_action("find", "world", "-c", "foo")
    assert record_messages.find(find.library_name("world"))

    record_messages.reset()
    qibuild_action("find", "hello", "-c", "foo")
    assert record_messages.find(find.binary_name("hello"))

    rc = qibuild_action("find", "libeggs", "-c", "foo", retcode=True)
    assert rc == 1

