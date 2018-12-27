#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test CMake Builder """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
from contextlib import contextmanager
from mock import patch
import pytest

import qibuild.config
import qibuild.parsers
import qibuild.cmake_builder


def test_check_configure_has_been_called_before_building(build_worktree):
    """ Test Check Configure Has Been Called Before Building """
    hello_proj = build_worktree.create_project("hello")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [hello_proj])
    with pytest.raises(qibuild.cmake_builder.NotConfigured):
        cmake_builder.build()


def test_default_install(build_worktree, toolchains, tmpdir):
    """ Test Default Install """
    hello_proj = build_worktree.create_project("hello", run_depends="bar")
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    build_worktree.set_active_config("foo")
    toolchains.add_package("foo", "bar")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [hello_proj])
    cmake_builder.configure()
    cmake_builder.build()
    cmake_builder.install(tmpdir.strpath)


def test_runtime_single(build_worktree, args):
    """ Test Runtime Single """
    build_worktree.create_project("hello", run_depends="bar")
    args.projects = ["hello"]
    args.runtime_only = True
    args.single = True
    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    assert cmake_builder.dep_types == []


def test_sdk_dirs(build_worktree):
    """ Test SDK Dirs """
    _foo_proj = build_worktree.create_project("foo")
    bar_proj = build_worktree.create_project("bar", build_depends=["foo"])
    baz_proj = build_worktree.create_project("baz", build_depends=["bar"])
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [bar_proj])
    sdk_dirs_when_top_project = cmake_builder.get_sdk_dirs_for_project(bar_proj)
    cmake_builder.projects = [baz_proj]
    sdk_dirs_when_not_top_project = cmake_builder.get_sdk_dirs_for_project(bar_proj)
    assert sdk_dirs_when_top_project == sdk_dirs_when_not_top_project


def test_add_package_paths_from_toolchain(build_worktree, toolchains, monkeypatch):
    """ Test Add Packages Path From Toolchain """
    toolchains.create("test")
    qibuild.config.add_build_config("test", toolchain="test")
    boost_package = toolchains.add_package("test", "boost")
    pthread_package = toolchains.add_package("test", "pthread")
    qi_package = toolchains.add_package("test", "libqi", build_depends=["boost"])
    naoqi_proj = build_worktree.create_project("naoqi", build_depends=["libqi"])
    build_worktree.set_active_config("test")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [naoqi_proj])
    sdk_dirs = cmake_builder.get_sdk_dirs_for_project(naoqi_proj)
    assert sdk_dirs == [boost_package.path, qi_package.path, pthread_package.path]
    monkeypatch.setenv("QIBUILD_STRICT_DEPS_RESOLUTION", "ON")
    sdk_dirs = cmake_builder.get_sdk_dirs_for_project(naoqi_proj)
    assert sdk_dirs == [boost_package.path, qi_package.path]


def test_host_tools_happy_path(build_worktree, fake_ctc):
    """ Test Host Tools Happy Path """
    footool = build_worktree.add_test_project("footool")
    footool.configure()
    host_sdk_dir = footool.sdk_directory
    usefootool_proj = build_worktree.add_test_project("usefootool")
    build_worktree.set_active_config("fake-ctc")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    host_dirs = cmake_builder.get_host_dirs(usefootool_proj)
    assert host_dirs == [host_sdk_dir]


def test_host_tools_no_host_config(build_worktree, fake_ctc):
    """ Test Host Tools No Host Config """
    _footool = build_worktree.add_test_project("footool")
    usefootool_proj = build_worktree.add_test_project("usefootool")
    build_worktree.set_active_config("fake-ctc")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    with pytest.raises(Exception) as e:
        cmake_builder.get_host_dirs(usefootool_proj)
    assert "`qibuild set-host-config`" in e.value.message


def test_host_tools_host_tools_not_built(build_worktree, fake_ctc):
    """ Test Host Tools Not Built """
    qibuild.config.add_build_config("foo", host=True)
    _footool = build_worktree.add_test_project("footool")
    usefootool_proj = build_worktree.add_test_project("usefootool")
    build_worktree.set_active_config("fake-ctc")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    with pytest.raises(Exception) as e:
        cmake_builder.get_host_dirs(usefootool_proj)
    assert "(Using 'foo' build config)" in e.value.message


@patch('qibuild.cmake_builder.ui')
@pytest.mark.skipif(sys.platform.startswith('win'), reason="Unavailable on Windows")
def test_post_install_dup_lib(ui, tmpdir):
    """ Test Post Install Dup Lib """
    all_files = {
        "JfufezF": [
            {"path": os.path.join('lib', 'asomething'), "role": "to_keep"},
            {"path": os.path.join('lib', 'what.so.1'), "role": "symlink", "target": "./what.so.1.2.3"},
            {"path": os.path.join('lib', 'truc.so'), "role": "symlink", "target": "./what.so.1.2.3"},
            {"path": os.path.join('lib', 'what.so.1.2.3'), "role": "to_keep"},
            {"path": os.path.join('not_lib', 'toto.so.3'), "role": "to_keep"}
        ],
        "w": [
            {"path": os.path.join('lib', 'nice.so'), "role": "already_symlink", "target": "./nice.so.4.3"},
            {"path": os.path.join('lib', 'nice.so.4'), "role": "already_symlink", "target": "./nice.so.4.3"},
            {"path": os.path.join('lib', 'nice.so.4.3'), "role": "to_keep"}
        ],
        "pJPG8IZ": [
            {"path": os.path.join('not_lib', 'toto.so'), "role": "to_keep"},
            {"path": os.path.join('not_lib', 'toto.so.2'), "role": "to_keep"},
            {"path": os.path.join('lib', 'other.so.1'), "role": "symlink", "target": "./other.so.old"},
            {"path": os.path.join('lib', 'other.so.old'), "role": "to_keep"}
        ],
        "#!/usr/bin/env python": [
            {"path": os.path.join('lib', 'python.py'), "role": "to_keep"},
            {"path": os.path.join('lib', 'python.pyc'), "role": "to_keep"},
            {"path": os.path.join('lib', 'python.pyo'), "role": "to_keep"}
        ],
    }
    with duplicated_lib_check(tmpdir.strpath, all_files) as input_files:
        output_files = qibuild.cmake_builder.CMakeBuilder("").post_install(tmpdir.strpath, input_files,
                                                                           replace_duplicated_lib_by_symlink=True,
                                                                           remove_python_bytecode=False)
        assert ui.warning.call_count == 0
        assert sorted(input_files) == sorted(output_files)


@contextmanager
def duplicated_lib_check(directory, all_files):
    """ Context manager to initiate directory struture and check after test """
    input_files = []
    for content, files in all_files.items():
        for fic in files:
            full_path = os.path.join(directory, fic['path'])
            if not os.path.exists(os.path.dirname(full_path)):
                os.makedirs(os.path.dirname(full_path))
            input_files.append(fic['path'])
            if fic['role'] == "already_symlink":
                os.symlink(fic['target'], full_path)  # pylint:disable=no-member
            else:
                with open(full_path, 'w') as ficp:
                    ficp.write(content)
    yield input_files
    for files in all_files.values():
        for fic in files:
            path = os.path.join(directory, fic['path'])
            if fic['role'] == 'to_keep':
                assert os.path.isfile(path)
            elif fic['role'] in ('symlink', "already_symlink"):
                assert os.path.islink(path)
                assert os.readlink(path) == fic['target']  # pylint:disable=no-member
            else:
                assert not os.path.exists(path)


def test_post_install_clean_python(tmpdir):
    """ Test Post Install Clean Python """
    all_files = {
        "JCVOIUEFZace8fufezF": [
            {"path": os.path.join('lib', 'asomething'), "role": "to_keep"},
            {"path": os.path.join('lib', 'what.so.1'), "role": "to_keep"},
            {"path": os.path.join('lib', 'truc.so'), "role": "to_keep"},
            {"path": os.path.join('lib', 'what.so.1.2.3'), "role": "to_keep"},
            {"path": os.path.join('not_lib', 'toto.so.3'), "role": "to_keep"}
        ],
        "pJPG8IZ90E8FUZEFEZF": [
            {"path": os.path.join('not_lib', 'toto.so'), "role": "to_keep"},
            {"path": os.path.join('not_lib', 'toto.so.2'), "role": "to_keep"},
            {"path": os.path.join('lib', 'other.so.1'), "role": "to_keep"},
            {"path": os.path.join('lib', 'other.so.old'), "role": "to_keep"}
        ],
        "#!/usr/bin/env python": [
            {"path": os.path.join('lib', 'python.py'), "role": "to_keep"},
            {"path": os.path.join('lib', 'python.pyc'), "role": "to_delete"},
            {"path": os.path.join('lib', 'python.pyo'), "role": "to_delete"}
        ],
    }
    with duplicated_lib_check(tmpdir.strpath, all_files) as input_files:
        output_files = qibuild.cmake_builder.CMakeBuilder("").post_install(tmpdir.strpath, input_files,
                                                                           replace_duplicated_lib_by_symlink=False,
                                                                           remove_python_bytecode=True)
        assert len(input_files) == len(output_files) + 2


@patch('qibuild.cmake_builder.ui')
@patch('qibuild.cmake_builder.sys')
def test_post_install_dup_lib_windows(mocked_sys, ui, tmpdir):
    """ Test Post Install Dup Lib Windows """
    mocked_sys.platform.return_value = 'windoze'
    all_files = {
        "JCVOIUE": [
            {"path": os.path.join('lib', 'asomething'), "role": "to_keep"},
            {"path": os.path.join('lib', 'what.so.1'), "role": "to_keep"},
            {"path": os.path.join('lib', 'truc.so'), "role": "to_keep"},
            {"path": os.path.join('lib', 'what.so.1.2.3'), "role": "to_keep"},
            {"path": os.path.join('not_lib', 'toto.so.3'), "role": "to_keep"},
        ],
        "pJPG8IZ": [
            {"path": os.path.join('not_lib', 'toto.so'), "role": "to_keep"},
            {"path": os.path.join('not_lib', 'toto.so.2'), "role": "to_keep"},
            {"path": os.path.join('lib', 'other.so.1'), "role": "to_keep"},
            {"path": os.path.join('lib', 'other.so.old'), "role": "to_keep"},
        ],
        "#!/usr/bin/env python": [
            {"path": os.path.join('lib', 'python.py'), "role": "to_keep"},
            {"path": os.path.join('lib', 'python.pyc'), "role": "to_keep"},
            {"path": os.path.join('lib', 'python.pyo'), "role": "to_keep"},
        ],
    }
    with duplicated_lib_check(tmpdir.strpath, all_files) as input_files:
        output_files = qibuild.cmake_builder.CMakeBuilder("").post_install(tmpdir.strpath, input_files + input_files,
                                                                           replace_duplicated_lib_by_symlink=True,
                                                                           remove_python_bytecode=False)
        assert sorted(input_files) == sorted(output_files)
        assert ui.warning.call_count == 1


def test_post_install_all_with_dup(tmpdir):
    """ Test Post Install All With Dup """
    all_files = {
        "JCVOIUE": [
            {"path": os.path.join('lib', 'asomething'), "role": "to_keep"},
            {"path": os.path.join('lib', 'what.so.1'), "role": "symlink", "target": "./what.so.1.2.3"},
            {"path": os.path.join('lib', 'truc.so'), "role": "symlink", "target": "./what.so.1.2.3"},
            {"path": os.path.join('lib', 'what.so.1.2.3'), "role": "to_keep"},
            {"path": os.path.join('not_lib', 'toto.so.3'), "role": "to_keep"},
        ],
        "pJPG8IZ": [
            {"path": os.path.join('not_lib', 'toto.so'), "role": "to_keep"},
            {"path": os.path.join('not_lib', 'toto.so.2'), "role": "to_keep"},
            {"path": os.path.join('lib', 'other.so.1'), "role": "symlink", "target": "./other.so.old"},
            {"path": os.path.join('lib', 'other.so.old'), "role": "to_keep"},
        ],
        "#!/usr/bin/env python": [
            {"path": os.path.join('lib', 'python.py'), "role": "to_keep"},
            {"path": os.path.join('lib', 'python.pyc'), "role": "to_delete"},
            {"path": os.path.join('lib', 'python.pyo'), "role": "to_delete"},
        ],
    }
    with duplicated_lib_check(tmpdir.strpath, all_files) as input_files:
        output_files = qibuild.cmake_builder.CMakeBuilder("").post_install(tmpdir.strpath, input_files + input_files,
                                                                           replace_duplicated_lib_by_symlink=True,
                                                                           remove_python_bytecode=True)
        assert len(input_files) == len(output_files) + 2
