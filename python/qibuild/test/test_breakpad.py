#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Breakpad """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import pytest

import qisys.command
import qibuild.find
import qibuild.breakpad
import qibuild.cmake_builder


@pytest.mark.skipif(not qisys.command.find_program("dump_syms"), reason="dump_syms not found")
def test_generate_symbols(build_worktree, tmpdir):
    """ Test Generate Symbols """
    build_worktree.add_test_project("world")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    build_config = cmake_builder.build_config
    build_config.build_type = "Release"
    build_config.user_flags = [("QI_WITH_DEBUG_INFO", "ON")]
    world_proj = build_worktree.get_build_project("world")
    cmake_builder.projects = [world_proj]
    cmake_builder.configure()
    cmake_builder.build()
    dest = tmpdir.join("dest").strpath
    cmake_builder.install(dest, components=["runtime"])
    symbols_archive = tmpdir.join("dest", "world.symbols.zip").strpath
    res = qibuild.breakpad.gen_symbol_archive(base_dir=dest, output=symbols_archive)
    assert os.path.exists(res)


def test_is_macho(qibuild_action):
    """ Test Is Macho """
    if sys.platform != "darwin":
        return
    world_project = qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")
    qibuild_action("make", "world")
    # world is dynamic, bar is static
    lib_world = qibuild.find.find_lib([world_project.sdk_directory], "world",
                                      expect_one=True)
    lib_bar = qibuild.find.find_lib([world_project.sdk_directory], "bar",
                                    expect_one=True)
    assert qibuild.breakpad.is_macho(lib_world)
    assert not qibuild.breakpad.is_macho(lib_bar)


def test_is_exe():
    """ Test Is Exe """
    assert qibuild.breakpad.is_exe("foo.exe")
    assert qibuild.breakpad.is_exe("foo.dll")
    assert not qibuild.breakpad.is_exe("foo.lib")
