#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Test QiBuild Add Config.
Check that every install() function returns a list of relative, POSIX paths.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.sh
import qibuild.config
import qitoolchain.qipackage


def test_install_project(qibuild_action, tmpdir):
    """ Test INstall Project """
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "--all")
    qibuild_action("make", "--all")
    dest = tmpdir.join("dest")
    ret = qibuild_action("install", "world", dest.strpath)
    assert "include/world/world.h" in ret


def test_install_modern_package_without_manifest(qitoolchain_action, qibuild_action, tmpdir):
    """ Test INstall Modern Package Without Manifest """
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
    print(ret)
    assert "bin/hello" in ret
    assert "lib/libworld.so" in ret


def test_install_modern_package_with_manifest(tmpdir):
    """ Test Install Modern Package With Manifest """
    boost_path = tmpdir.mkdir("boost")
    boost_path.ensure("include", "boost.h", file=True)
    boost_path.ensure("lib", "libboost.so", file=True)
    runtime_manifest = boost_path.ensure("install_manifest_runtime.txt", file=True)
    runtime_manifest.write("""lib/libboost.so\n""")
    package = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    dest = tmpdir.join("dest")
    installed = package.install(dest.strpath, components=["runtime"])
    assert installed == ["lib/libboost.so"]
