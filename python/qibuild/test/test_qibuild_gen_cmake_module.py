## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.archive
import qisys.sh
import qibuild.config
import qitoolchain.qipackage

def test_simple(qibuild_action, toolchains, tmpdir, record_messages):
    test_tc = toolchains.create("test")
    qibuild.config.add_build_config("test", toolchain="test")
    foo = tmpdir.mkdir("foo")
    foo.ensure("include", "foo.h", file=True)
    libfoo = foo.ensure("lib", "libfoo.so", file=True)
    libfoobar = foo.ensure("lib", "libfoobar.so", file=True)
    libfoobaz = foo.ensure("lib", "libfoobaz.so", file=True)
    qibuild_action("gen-cmake-module", "--name", "foo", foo.strpath)
    foo_config = foo.join("share", "cmake", "foo", "foo-config.cmake")
    assert foo_config.check(file=True)
    foo.join("package.xml").write("""
<package name="foo" version="0.1" />
""")
    foo_archive = qisys.archive.compress(foo.strpath, flat=True)
    foo_package = qitoolchain.qipackage.from_archive(foo_archive)
    foo_package.path = foo.strpath
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
    actual_list = value.split(";")
    # Need to resolve symlinks:
    actual_list = [os.path.realpath(x) for x in actual_list]
    expected_list = [libfoo.strpath, libfoobar.strpath, libfoobaz.strpath]
    for actual_path, expected_path in zip(actual_list, expected_list):
        assert qisys.sh.samefile(actual_path, expected_path)
