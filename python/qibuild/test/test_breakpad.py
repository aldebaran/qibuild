## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import pytest

import qisys.command
import qibuild.breakpad
import qibuild.cmake_builder


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
    installed_files = cmake_builder.install(dest, components=["runtime"])
    symbols_archive = tmpdir.join("dest", "world.symbols.zip").strpath
    res = qibuild.breakpad.gen_symbol_archive(world_proj, base_dir=dest,
                                              output=symbols_archive,
                                              file_list=installed_files)
    assert os.path.exists(res)
