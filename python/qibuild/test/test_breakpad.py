## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import sys

import pytest

import qisys.command
import qibuild.breakpad
import qibuild.cmake_builder
import qibuild.find


# pylint: disable-msg=E1101
@pytest.mark.skipif(not qisys.command.find_program("dump_syms"),
                    reason="dump_syms not found")
def test_generate_symbols(build_worktree, tmpdir):
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
    if not sys.platform == "darwin":
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
    assert qibuild.breakpad.is_exe("foo.exe")
    assert qibuild.breakpad.is_exe("foo.dll")
    assert not qibuild.breakpad.is_exe("foo.lib")
