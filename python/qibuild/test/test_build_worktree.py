## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import sys

import qisys.error
import qibuild.config

from qibuild.test.conftest import TestBuildWorkTree
from qitoolchain.test.conftest import toolchains
from qipy.test.conftest import qipy_action

import pytest

def test_read_deps(build_worktree):
    build_worktree.create_project("world")
    build_worktree.create_project("hello", build_depends=["world"])
    hello = build_worktree.get_build_project("hello")
    assert hello.build_depends == set(["world"])

def test_new_syntax(build_worktree):
    world_proj = build_worktree.create_project("world")
    with open(world_proj.qiproject_xml, "w") as fp:
        fp.write("""
<project format="3">
  <version>0.42</version>
  <qibuild name="world" />
</project>
""")
    build_worktree = TestBuildWorkTree()
    world_proj = build_worktree.get_build_project("world")
    assert world_proj.name == "world"
    assert world_proj.version == "0.42"

def test_setting_build_config_sets_projects_cmake_flags(build_worktree):
    build_worktree.create_project("world")
    build_worktree.build_config.build_type = "Release"
    world = build_worktree.get_build_project("world")
    cmake_args = world.cmake_args
    assert "-DCMAKE_BUILD_TYPE=Release" in cmake_args

def test_changing_active_config_changes_projects_build_dir(cd_to_tmpdir):
    qibuild.config.add_build_config("foo")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("foo")
    world_proj = build_worktree.create_project("world")
    assert "foo" in  world_proj.build_directory

def test_project_names_are_unique(build_worktree):
    build_worktree.create_project("foo")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        build_worktree.create_project("foo", src="bar/foo")
    assert "two projects with the same name" in str(e.value)

def test_bad_qibuild2_qiproject(cd_to_tmpdir):
    build_worktree = TestBuildWorkTree()
    build_worktree.create_project("foo")
    foo_qiproj_xml = build_worktree.tmpdir.join("foo").join("qiproject.xml")
    foo_qiproj_xml.write(""" \
<project name="foo">
    <project src="bar" />
</project>
""")
    bar_path = build_worktree.tmpdir.join("foo", "bar").ensure(dir=True)
    bar_path.ensure("CMakeLists.txt").ensure(file=True)
    bar_qiproj_xml = bar_path.join("qiproject.xml")
    bar_qiproj_xml.write("<project />")
    build_worktree = TestBuildWorkTree()

def test_set_default_config(cd_to_tmpdir):
    qibuild.config.add_build_config("foo")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_default_config("foo")
    assert build_worktree.default_config == "foo"
    build_worktree2 = TestBuildWorkTree()
    assert build_worktree2.default_config == "foo"

def test_get_env(toolchains, cd_to_tmpdir):
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    bar_package = toolchains.add_package("foo", "bar")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("foo")
    world_proj = build_worktree.create_project("world")
    env = build_worktree.get_env()
    if sys.platform.startswith("linux"):
        assert env["LD_LIBRARY_PATH"] == "%s:%s" % (
                os.path.join(world_proj.sdk_directory, "lib"),
                os.path.join(bar_package.path, "lib"))
    if sys.platform.startswith("win"):
        old_path = os.environ["PATH"]
        assert env["PATH"] == "%s;%s;%s" % (
                os.path.join(world_proj.sdk_directory, "bin"),
                os.path.join(bar_package.path, "bin"),
                old_path)
    if sys.platform == "darwin":
        assert env["DYLD_LIBRARY_PATH"] == "%s:%s" % (
                os.path.join(world_proj.sdk_directory, "lib"),
                os.path.join(bar_package.path, "lib"))
        assert env["DYLD_FRAMEWORK_PATH"] == bar_package.path

def test_set_pythonhome(toolchains, cd_to_tmpdir):
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    python_package = toolchains.add_package("foo", "python")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("foo")
    env = build_worktree.get_env()
    if sys.platform == "darwin":
        assert env["PYTHONHOME"] == python_package.path + "/Python.framework/Versions/2.7"
    else:
        assert env["PYTHONHOME"] == python_package.path

def test_venv_path(qipy_action):
    qipy_action("bootstrap")
    build_worktree = TestBuildWorkTree()
    venv_path = build_worktree.venv_path
    if os.name == "nt":
        bin_dir = "Scripts"
    else:
        bin_dir = "bin"
    activate = os.path.join(venv_path, bin_dir, "activate")
    assert os.path.exists(activate)
