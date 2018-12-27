#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Gen CMake Module """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.archive
import qibuild.config
import qitoolchain.qipackage


def test_simple(qibuild_action, toolchains, tmpdir, record_messages):
    """ Test Simple """
    test_tc = toolchains.create("test")
    qibuild.config.add_build_config("test", toolchain="test")
    foo1 = tmpdir.mkdir("foo")
    foo1.ensure("include", "foo.h", file=True)
    libfoo = foo1.ensure("lib", "libfoo.so", file=True)
    libfoobar = foo1.ensure("lib", "libfoobar.so", file=True)
    libfoobaz = foo1.ensure("lib", "libfoobaz.so", file=True)
    qibuild_action("gen-cmake-module", "--name", "foo", foo1.strpath)
    foo_config = foo1.join("share", "cmake", "foo", "foo-config.cmake")
    assert foo_config.check(file=True)
    foo1.join("package.xml").write("""\n<package name="foo" version="0.1" />\n""")
    foo_archive = qisys.archive.compress(foo1.strpath, flat=True)
    foo_package = qitoolchain.qipackage.from_archive(foo_archive)
    foo_package.path = foo1.strpath
    test_tc.add_package(foo_package)
    bar_proj = qibuild_action.create_project("bar", build_depends=["foo"])
    cmake_lists = os.path.join(bar_proj.path, "CMakeLists.txt")
    with open(cmake_lists, "a") as fp:
        fp.write("qi_use_lib(bar FOO)\n")
    qibuild_action("configure", "bar", "--config", "test")
    record_messages.reset()
    with qisys.sh.change_cwd(bar_proj.path):
        qibuild_action("find", "--cmake", "foo", "--config", "test")
    foo_lib = record_messages.find("FOO_LIBRARIES")
    value = foo_lib.split()[1]
    splitted = value.split(";")
    assert splitted == [libfoo.strpath, libfoobar.strpath, libfoobaz.strpath]
