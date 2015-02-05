## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qisys.archive
import qitoolchain
import qibuild.config

def test_simple(qitoolchain_action):
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    word_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo",  word_package)
    tc = qitoolchain.get_toolchain("foo")
    world_package = tc.packages[0]
    assert world_package.name == "world"
    assert world_package.path

def test_legacy_no_name_given(tmpdir, qitoolchain_action):
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    world = tmpdir.mkdir("world")
    world.ensure("include", "world.h", file=True)
    world.ensure("lib", "libworld.so", file=True)
    archive = qisys.archive.compress(world.strpath)
    error = qitoolchain_action("add-package", "-c", "foo", archive, raises=True)
    assert "Must specify --name" in error

def test_legacy_happy_path(tmpdir, qitoolchain_action):
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    world = tmpdir.mkdir("world")
    world.ensure("include", "world.h", file=True)
    world.ensure("lib", "libworld.so", file=True)
    archive = qisys.archive.compress(world.strpath)
    qitoolchain_action("add-package", "-c", "foo", "--name", "world", archive)
    tc = qitoolchain.get_toolchain("foo")
    world_package = tc.get_package("world")
    assert os.path.exists(os.path.join(world_package.path, "include", "world.h"))
    assert os.path.exists(os.path.join(world_package.path, "lib", "libworld.so"))
