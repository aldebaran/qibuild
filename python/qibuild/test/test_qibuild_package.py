#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest

import qisys.archive
import qisrc.license
import qibuild.config
from qibuild.test.conftest import QiBuildAction
import qitoolchain.qipackage
from qitoolchain.test.conftest import QiToolchainAction


def test_simple(qibuild_action):
    """ Test Simple """
    qibuild_action.add_test_project("world")
    world_archive = qibuild_action("package", "world")
    assert os.path.exists(world_archive)
    qipackage = qitoolchain.qipackage.from_archive(world_archive)
    assert qipackage.name == "world"


def test_building_in_release(qibuild_action):
    """ Test Building In Release """
    qibuild_action.add_test_project("world")
    qibuild_action("package", "world", "--release")


def test_using_toolchain(cd_to_tmpdir):
    """ Test Using Toolchain """
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
    # this should now fail (no world-config.cmake found)
    qibuild_action("configure", "hello", raises=True)
    # but this should pass:
    qibuild_action("configure", "-c", "foo", "hello")


def test_preserve_license(qibuild_action, qitoolchain_action):
    """ Test Preserve Licence """
    world_proj = qibuild_action.add_test_project("world")
    qisrc.license.write_license(world_proj.qiproject_xml, "BSD")
    world_package = qibuild_action("package", "world")
    extracted = qitoolchain_action("extract-package", world_package)
    package_xml = os.path.join(extracted, "package.xml")
    license_name = qisrc.license.read_license(package_xml)
    assert license_name == "BSD"


def test_standalone(qibuild_action, tmpdir):
    """ Test Standalone """
    _world_proj = qibuild_action.add_test_project("world")
    _hello_proj = qibuild_action.add_test_project("hello")
    hello_archive = qibuild_action("package", "hello", "--standalone")
    # Make sure bin/hello can run after extracting the standalone package
    dest = tmpdir.join("dest")
    extracted = qisys.archive.extract(hello_archive, dest.strpath)
    hello_bin = os.path.join(extracted, "bin", "hello")
    qisys.command.call([hello_bin])


@pytest.mark.skipif(not qisys.command.find_program("dump_syms"), reason="dump_syms not found")
def test_standalone_breakpad(qibuild_action, tmpdir):
    """ Test Standalone Breakpad """
    _world_proj = qibuild_action.add_test_project("world")
    _hello_proj = qibuild_action.add_test_project("hello")
    _hello_archive, hello_symbols = qibuild_action(
        "package", "hello", "--standalone", "--breakpad"
    )
    assert os.path.exists(hello_symbols)
