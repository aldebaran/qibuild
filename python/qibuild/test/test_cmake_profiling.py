# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import os

import qisys.sh
import qibuild.cmake

from qibuild.cmake.profiling import parse_cmake_log
from qibuild.cmake.profiling import gen_annotations


def test_simple_parse(tmpdir):
    out = """Running with trace output on.
@worktree@/lib/gtest/CMakeLists.txt(3):  cmake_minimum_required(VERSION 2.8 )
@worktree@/lib/gtest/CMakeLists.txt(4):  project(gtest )
/usr/share/cmake-2.8/Modules/CMakeUnixFindMake.cmake(15):  FIND_PROGRAM(CMAKE_MAKE_PROGRAM NAMES gmake make smake )
/usr/share/cmake-2.8/Modules/CMakeUnixFindMake.cmake(16):  MARK_AS_ADVANCED(CMAKE_MAKE_PROGRAM )
@worktree@/lib/gtest/build-sys-linux-x86_64/CMakeFiles/CMakeSystem.cmake(3):  SET(CMAKE_SYSTEM Linux-3.4.8-1-ARCH )
@qibuild_root@/qibuild/internal/install.cmake(64):  install(FILES ${_file} COMPONENT ${ARG_COMPONENT} DESTINATION ${ARG_DESTINATION}/${ARG_SUBFOLDER}/${_file_subdir} )
@qibuild_root@/qibuild/internal/stage.cmake(73):  set(_deps ${ARG_DEPENDS} )
@qibuild_root@/qibuild/internal/stage.cmake(74):  set(_dest_dir ${CMAKE_BINARY_DIR}/redist-cmake )
@qibuild_root@/qibuild/internal/install.cmake(63):  get_filename_component(_file_subdir ${_file} PATH )
@qibuild_root@/qibuild/internal/install.cmake(63):  get_filename_component(_file_subdir ${_file} PATH )
"""  # noqa
    qibuild_dir = qibuild.cmake.get_cmake_qibuild_dir()
    qibuild_dir = qisys.sh.to_posix_path(qibuild_dir)
    if os.name == 'nt':
        out = out.replace("@worktree@", "c:/path/to/worktree")
    else:
        out = out.replace("@worktree@", "/path/to/worktree")
    out = out.replace("@qibuild_root@", qibuild_dir)
    cmake_log = tmpdir.join("cmake.log")
    cmake_log.write(out)

    profile = parse_cmake_log(cmake_log.strpath, qibuild_dir)
    assert profile["internal/stage.cmake"] == {73: 1, 74: 1}
    assert profile["internal/install.cmake"] == {64: 1, 63: 2}


def test_gen_annotations(tmpdir):
    profile = {
        "internal/stage.cmake": {1: 3, 2: 39},
        "internal/install.cmake": {3: 3},
    }
    qibuild_dir = qibuild.cmake.get_cmake_qibuild_dir()
    gen_annotations(profile, tmpdir.strpath, qibuild_dir)
    stage_lines = tmpdir.join("internal/stage.cmake").read().splitlines()
    assert stage_lines[0].startswith(" 3")
    assert stage_lines[1].startswith("39")
    assert stage_lines[2].startswith("  ")
