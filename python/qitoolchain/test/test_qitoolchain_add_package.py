#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Toolchain Add Package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import re

import qisys.archive
import qibuild.config
import qitoolchain
from qitoolchain.test.conftest import qitoolchain_action


def test_simple(qitoolchain_action):
    """ Test Simple """
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    word_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo", word_package)
    tc = qitoolchain.get_toolchain("foo")
    world_package = tc.packages[0]
    assert world_package.name == "world"
    assert world_package.path


def test_legacy_no_name_given(tmpdir, qitoolchain_action):
    """ Test Legacy No Name Given """
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    world = tmpdir.mkdir("world")
    world.ensure("include", "world.h", file=True)
    world.ensure("lib", "libworld.so", file=True)
    archive = qisys.archive.compress(world.strpath)
    error = qitoolchain_action("add-package", "-c", "foo", archive, raises=True)
    assert "Must specify --name" in error


def test_legacy_happy_path(tmpdir, qitoolchain_action):
    """ Test Legacy Happy Path """
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
    """ Test Flags Package """
    qitoolchain_action("create", "foo")
    c11_flags = tmpdir.mkdir("c++11-flags")
    c11_flags.join("config.cmake").write("""\nset(CMAKE_CXX_FLAGS "-std=gnu++11")\n""")
    c11_flags.join("package.xml").write("""\n<package name="c++11-flags" toolchain_file="config.cmake" />\n""")
    flags_package = tmpdir.join("c++11-flags.zip")
    qisys.archive.compress(c11_flags.strpath, output=flags_package.strpath, flat=True)
    qitoolchain_action("add-package", "--toolchain", "foo", flags_package.strpath)
    foo_toolchain = qitoolchain.get_toolchain("foo")
    tc_file = foo_toolchain.toolchain_file
    with open(tc_file, "r") as fp:
        contents = fp.read()
    included_file = None
    for line in contents.splitlines():
        match = re.match(r'include\("(.*)"\)', line)
        if match:
            included_file = match.groups()[0]
    assert os.path.exists(included_file)
