import sys
import os

import qisys.command

import qibuild.find

from qisys.test.conftest import skip_on_win
from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_running_from_install_dir_dep_in_worktree(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "--runtime", "hello", tmpdir.strpath)

    hello = qibuild.find.find_bin([tmpdir.strpath], "hello")
    qisys.command.call([hello])

    assert not tmpdir.join("include").check()

def test_running_from_install_dir_dep_in_toolchain(cd_to_tmpdir):
    # create a foo toolchain containing the world package
    qibuild_action = QiBuildAction()
    qitoolchain_action = QiToolchainAction()
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qitoolchain_action("add-package", "-c", "foo", "world", world_package)
    build_worktree.worktree.remove_project("world", from_disk=True)

    # install and run hello, (checking that the world lib is
    # installed form the package of the toolchain)
    qibuild_action("configure", "-c", "foo", "hello")
    qibuild_action("make", "-c", "foo", "hello")
    prefix = cd_to_tmpdir.mkdir("prefix")
    qibuild_action("install", "-c", "foo", "hello", prefix.strpath)

    hello = qibuild.find.find_bin([prefix.strpath], "hello")
    qisys.command.call([hello])


def test_devel_components_installed_by_default(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "hello", tmpdir.strpath)
    assert tmpdir.join("include").join("world").join("world.h").check()

def test_setting_prefix(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "--prefix=/usr", "--runtime",
                   "hello", tmpdir.strpath)
    hello = qibuild.find.find([tmpdir.join("usr").strpath], "hello")

def test_using_compiled_tool_for_install(qibuild_action, tmpdir):
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("bar")
    qibuild_action("configure", "bar")
    qibuild_action("make", "bar")
    qibuild_action("install", "bar", tmpdir.strpath)

    foo_out = tmpdir.join("share", "foo", "foo.out")
    assert foo_out.check(file=True)

def test_compile_data(qibuild_action, tmpdir):
    qibuild_action.add_test_project("compile_data")
    qibuild_action("configure", "compile_data")
    qibuild_action("make", "compile_data")
    qibuild_action("install", "compile_data", tmpdir.strpath)
    assert tmpdir.join("share", "foo.out").check(file=True)

def test_failing_compiler_makes_install_fail(qibuild_action, tmpdir):
    qibuild_action.add_test_project("compile_data")
    qibuild_action("configure", "compile_data", "-DFAIL_COMPILER=ON")
    qibuild_action("make", "compile_data")
    error = qibuild_action("install", "compile_data", tmpdir.strpath, raises=True)
    assert error

def test_qi_install_cmake(qibuild_action, tmpdir):
    qibuild_action.add_test_project("installme")
    qibuild_action("configure", "installme")
    qibuild_action("make", "installme")
    qibuild_action("install", "installme", tmpdir.strpath)
    assert tmpdir.join("share", "data_star", "foo.dat").check(file=True)
    assert tmpdir.join("share", "data_star", "bar.dat").check(file=True)
    assert tmpdir.join("share", "recurse", "a_dir/a_file").check(file=True)
    assert tmpdir.join("share", "recurse", "a_dir/b_dir/c_dir/d_file").check(file=True)

def test_fails_early(qibuild_action, tmpdir):
    qibuild_action.add_test_project("installme")
    qibuild_action("configure", "installme", "-DFAIL_EMPTY_GLOB=TRUE", raises=True)
    qibuild_action("configure", "installme", "-DFAIL_NON_EXISTING=TRUE", raises=True)


def test_install_cross_unix_makefiles(qibuild_action, tmpdir):
    install_cross(qibuild_action, tmpdir, cmake_generator="Unix Makefiles")

def test_install_cross_ninja(qibuild_action, tmpdir):
    install_cross(qibuild_action, tmpdir, cmake_generator="Ninja")

@skip_on_win
def install_cross(qibuild_action, tmpdir, cmake_generator="Unix Makefiles"):
    cross_proj = qibuild_action.add_test_project("cross")
    toolchain_file = os.path.join(cross_proj.path, "toolchain.cmake")
    qibuild_action("configure", "cross",
                   "-G", cmake_generator,
                   "-DCMAKE_TOOLCHAIN_FILE=%s" % toolchain_file)
    qibuild_action("make", "cross",)
    qibuild_action("install", "cross",  tmpdir.strpath)
