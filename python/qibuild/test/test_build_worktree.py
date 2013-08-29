import os

from qibuild.test.conftest import TestBuildWorkTree

import pytest

def test_read_deps(build_worktree):
    build_worktree.create_project("world")
    build_worktree.create_project("hello", build_depends=["world"])
    hello = build_worktree.get_build_project("hello")
    assert hello.build_depends == set(["world"])

def test_setting_build_config_sets_projects_cmake_flags(build_worktree):
    build_worktree.create_project("world")
    build_worktree.build_config.build_type = "Release"
    world = build_worktree.get_build_project("world")
    assert world.cmake_args == ["-DCMAKE_BUILD_TYPE=Release"]

def test_setting_build_config_sets_projects_build_dir(build_worktree):
    build_worktree.create_project("world")
    build_worktree.build_config.build_type = "Release"
    world = build_worktree.get_build_project("world")
    assert "-release" in os.path.basename(world.build_directory)

def test_changing_active_config_changes_projects_build_dir(build_worktree, toolchains):
    world_proj = build_worktree.create_project("world")
    toolchains.create("foo")
    build_worktree.set_active_config("foo")
    assert "foo" in  world_proj.build_directory

def test_project_names_are_unique(build_worktree):
    build_worktree.create_project("foo")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
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
