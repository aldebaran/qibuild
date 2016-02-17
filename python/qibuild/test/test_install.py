## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Check that every install() function returns a list
# of relative, POSIX paths

import os

import qisys.sh
import qibuild.config
import qibuild.find
import qitoolchain.qipackage

def test_install_project(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "--all")
    qibuild_action("make", "--all")
    dest = tmpdir.join("dest")
    ret = qibuild_action("install", "world", dest.strpath)
    assert "include/world/world.h" in ret

def test_install_modern_package_without_manifest(qitoolchain_action,
        qibuild_action, tmpdir):
    qitoolchain_action("create", "test")
    qibuild.config.add_build_config("test", toolchain="test")
    world_proj = qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("add-package", "--toolchain", "test", world_package)

    qisys.sh.rm(world_proj.path)
    qibuild_action("configure", "--config", "test", "hello")
    qibuild_action("make", "--config", "test", "hello")
    dest = tmpdir.join("dest")
    ret = qibuild_action("install", "--runtime", "--config", "test", "hello", dest.strpath)
    libworld = qibuild.find.find_lib([dest.strpath], "world")
    libworld = os.path.relpath(libworld, dest.strpath)
    libworld = qisys.sh.to_posix_path(libworld)
    hello = qibuild.find.find_bin([dest.strpath], "hello")
    hello = os.path.relpath(hello, dest.strpath)
    hello = qisys.sh.to_posix_path(hello)
    assert hello in ret
    assert libworld in ret

def test_install_modern_package_with_manifest(tmpdir):
    boost_path = tmpdir.mkdir("boost")
    boost_path.ensure("include", "boost.h", file=True)
    boost_path.ensure("lib", "libboost.so", file=True)
    runtime_manifest = boost_path.ensure("install_manifest_runtime.txt", file=True)
    runtime_manifest.write("""\
lib/libboost.so
""")
    package = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    dest = tmpdir.join("dest")
    installed = package.install(dest.strpath, components=["runtime"])
    assert installed == ["lib/libboost.so"]
