## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import py

import qibuild.cmake

from qisys.test.conftest import skip_on_win

def test_get_cmake_qibuild_dir_no_worktree():
    res = qibuild.cmake.get_cmake_qibuild_dir()
    assert os.path.exists(os.path.join(res, "qibuild/general.cmake"))

def test_pip_std_install(tmpdir):
    python_dir = tmpdir.join("lib", "python2.7", "site-packages", "qibuild")
    python_dir.ensure("__init__.py", file=True)
    cmake_dir = tmpdir.join("share", "cmake")
    cmake_dir.ensure("qibuild", "qibuild-config.cmake", file=True)
    res = qibuild.cmake.find_installed_cmake_qibuild_dir(python_dir.strpath)
    assert res == cmake_dir.strpath

@skip_on_win
def test_pip_debian_install(tmpdir):
    local = tmpdir.mkdir("local")
    lib = tmpdir.mkdir("lib")
    local.join("lib").mksymlinkto(lib)
    python_dir = tmpdir.join("local", "lib", "python2.7", "site-packages", "qibuild")
    python_dir.ensure("__init__.py", file=True)
    cmake_dir = tmpdir.join("share", "cmake")
    cmake_dir.ensure("qibuild", "qibuild-config.cmake", file=True)
    res = qibuild.cmake.find_installed_cmake_qibuild_dir(python_dir.strpath)
    assert res == cmake_dir.strpath
