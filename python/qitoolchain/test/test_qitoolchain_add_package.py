## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import re

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

def test_flags_package(tmpdir, qitoolchain_action):
    qitoolchain_action("create", "foo")
    c11_flags = tmpdir.mkdir("c++11-flags")
    c11_flags.join("config.cmake").write("""
set(CMAKE_CXX_FLAGS "-std=gnu++11")
""")
    c11_flags.join("package.xml").write("""
<package name="c++11-flags" toolchain_file="config.cmake" />
""")
    flags_package = tmpdir.join("c++11-flags.zip")
    qisys.archive.compress(c11_flags.strpath, output=flags_package.strpath, flat=True)
    qitoolchain_action("add-package", "--toolchain", "foo", flags_package.strpath)
    foo_toolchain = qitoolchain.get_toolchain("foo")
    tc_file = foo_toolchain.toolchain_file
    with open(tc_file, "r") as fp:
        contents = fp.read()
    included_file = None
    for line in contents.splitlines():
        match = re.match('include\("(.*)"\)', line)
        if match:
            included_file = match.groups()[0]
    assert os.path.exists(included_file)
