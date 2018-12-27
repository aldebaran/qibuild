#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test CMake """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import mock
import pytest

import qibuild.cmake
from qisys.test.conftest import skip_on_win


def test_get_cmake_qibuild_dir_no_worktree():
    """ Test Get CMake QiBuild Dir No Worktree """
    res = qibuild.cmake.get_cmake_qibuild_dir()
    assert os.path.exists(os.path.join(res, "qibuild/general.cmake"))


def test_pip_std_install(tmpdir):
    """ Test Pip Standard Install """
    python_dir = tmpdir.join("lib", "python2.7", "site-packages", "qibuild")
    python_dir.ensure("__init__.py", file=True)
    cmake_dir = tmpdir.join("share", "cmake")
    cmake_dir.ensure("qibuild", "qibuild-config.cmake", file=True)
    res = qibuild.cmake.find_installed_cmake_qibuild_dir(python_dir.strpath)
    assert res == cmake_dir.strpath


@skip_on_win
def test_pip_debian_install(tmpdir):
    """ Test Pip Debian Install """
    local = tmpdir.mkdir("local")
    lib = tmpdir.mkdir("lib")
    local.join("lib").mksymlinkto(lib)
    python_dir = tmpdir.join("local", "lib", "python2.7", "site-packages", "qibuild")
    python_dir.ensure("__init__.py", file=True)
    cmake_dir = tmpdir.join("share", "cmake")
    cmake_dir.ensure("qibuild", "qibuild-config.cmake", file=True)
    res = qibuild.cmake.find_installed_cmake_qibuild_dir(python_dir.strpath)
    assert res == cmake_dir.strpath


def test_check_root_cmake_no_cmake_minimum_required(tmpdir):
    """ Test Check Root CMake No CMake Minimum Required """
    cmake_list = tmpdir.join("CMakeLists.txt")
    cmake_list.write("""\nproject(foo)\nfind_package(qibuild)\n""")
    with pytest.raises(qibuild.cmake.IncorrectCMakeLists) as e:
        qibuild.cmake.check_root_cmake_list(cmake_list.strpath)
    assert "Missing call to cmake_minimum_required" in e.value.message


def test_check_root_cmake_find_package_before_project(tmpdir):
    """ Test Check Root CMake Find Package Before Project """
    cmake_list = tmpdir.join("CMakeLists.txt")
    cmake_list.write("""
cmake_minimum_required(VERSION 2.8)
find_package(qibuild)
project(foo)
""")
    with pytest.raises(qibuild.cmake.IncorrectCMakeLists) as e:
        qibuild.cmake.check_root_cmake_list(cmake_list.strpath)
    assert "The call to find_package(qibuild) should be AFTER" in e.value.message


def test_check_root_cmake_no_project(tmpdir):
    """ Test Check Root CMake No Project """
    cmake_list = tmpdir.join("CMakeLists.txt")
    cmake_list.write("""\ncmake_minimum_required(VERSION 2.8)\nfind_package(qibuild)\n""")
    with pytest.raises(qibuild.cmake.IncorrectCMakeLists) as e:
        qibuild.cmake.check_root_cmake_list(cmake_list.strpath)
    assert "Missing call to project()" in e.value.message


def test_get_known_generators():
    """ Test Get Known Generators """
    with mock.patch("subprocess.Popen") as mock_popen:
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = ("""
Usage

    cmake [options] <path-to-source>
    cmake [options] <path-to-existing-build>

Options

Generators

The following generators are available on this platform:
  Unix Makefiles              = Generates standard UNIX makefiles.
  Ninja                       = Generates build.ninja files (experimental).
  Sublime Text 2 - Unix Makefiles
                              = Generates Sublime Text 2 project files.
""", "")
        with mock.patch("qisys.command.find_program") as mock_find_program:
            mock_find_program.return_value = '/usr/bin/cmake'
            res = qibuild.cmake.get_known_cmake_generators()
        call_args_list = mock_popen.call_args_list
        assert "cmake" in call_args_list[0][0][0][0]
        assert call_args_list[0][0][0][1] == "--help"
        assert mock_process.communicate.call_args_list == [mock.call()]
        assert res == ["Unix Makefiles", "Ninja", "Sublime Text 2 - Unix Makefiles"]


def test_generators_on_windows_cmake_3_3():
    """ Test Generators On Window CMake 3.3 """
    with mock.patch("subprocess.Popen") as mock_popen:
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = ("""
The following generators are available on this platform:
  Visual Studio 14 2015 [arch] = Generates Visual Studio 2015 project files
                                 Optional [arch] can be "Win64" or "ARM".
  Visual Studio 12 2013 [arch] = Generates Visual Studio 2013 project files
                                 Optional [arch] can be "Win64" or "ARM".
  Borland Makefiles            = Generates Borland makefiles.
""", "")
        with mock.patch("qisys.command.find_program") as mock_find_program:
            mock_find_program.return_value = 'c://cmake'
            res = qibuild.cmake.get_known_cmake_generators()
        assert res == ["Visual Studio 14 2015",
                       "Visual Studio 14 2015 Win64",
                       "Visual Studio 14 2015 ARM",
                       "Visual Studio 12 2013",
                       "Visual Studio 12 2013 Win64",
                       "Visual Studio 12 2013 ARM",
                       "Borland Makefiles"]
