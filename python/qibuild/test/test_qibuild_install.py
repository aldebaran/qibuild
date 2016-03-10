## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import sys
import os
import subprocess

import qisys.command
import qitest.project
import qibuild.config
import qibuild.find

from qisys.test.conftest import skip_on_win
from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def create_foo_toolchain_with_world_package(qibuild_action, qitoolchain_action):
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    qitoolchain_action("add-package", "-c", "foo", world_package)
    build_worktree.worktree.remove_project("world", from_disk=True)

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

    create_foo_toolchain_with_world_package(qibuild_action, qitoolchain_action)

    # install and run hello, (checking that the world lib is
    # installed form the package of the toolchain)
    qibuild_action("configure", "-c", "foo", "hello")
    qibuild_action("make", "-c", "foo", "hello")
    prefix = cd_to_tmpdir.mkdir("prefix")
    qibuild_action("install", "-c", "foo", "hello", prefix.strpath)

    hello = qibuild.find.find_bin([prefix.strpath], "hello")
    qisys.command.call([hello])

def test_libsubfolder(qibuild_action, tmpdir):
    dest = tmpdir.join("dest")
    qibuild_action.add_test_project("libsubfolder")
    qibuild_action("configure", "libsubfolder")
    qibuild_action("make", "libsubfolder")
    qibuild_action("install", "libsubfolder", dest.strpath)
    env_setter = qisys.envsetter.EnvSetter()
    # Make sure bar binary can run:
    # (On Windows, need to fix %PATH%
    if os.name == 'nt':
        env_setter.prepend_to_path(dest.join("lib", "foo").strpath)
    env = env_setter.get_build_env()
    bar = qibuild.find.find_bin([dest.strpath], "bar")
    qisys.command.call([bar], env=env)
    # Make sure foo-config.cmake is correct
    foo_config_cmake = dest.join("share", "cmake", "foo", "foo-config.cmake")
    to_write = "\nmessage(STATUS \"${FOO_LIBRARIES}\")\n"
    foo_config_cmake.write(to_write, mode="a")
    cmd = ["cmake", "-P", foo_config_cmake.strpath]
    output = subprocess.check_output(cmd)
    if os.name == "nt":
        # output looks like:
        # -- debug;/path/to/foo_d.lib;optimized;/path/to/foo.lib
        libs_from_cmake = output.split( )[1].split(";")[1]
    else:
        # output looks like:
        # -- /path/to/libfoo.so
        libs_from_cmake = output.split()[1]
    assert os.path.exists(libs_from_cmake)

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


@skip_on_win
def test_install_cross_unix_makefiles(qibuild_action, tmpdir):
    install_cross(qibuild_action, tmpdir, cmake_generator="Unix Makefiles")

@skip_on_win
def test_install_cross_ninja(qibuild_action, tmpdir):
    install_cross(qibuild_action, tmpdir, cmake_generator="Ninja")

def install_cross(qibuild_action, tmpdir, cmake_generator="Unix Makefiles"):
    if cmake_generator == "Ninja":
        ninja = qisys.command.find_program("ninja", raises=False)
        if not ninja:
            print "Ninja not installed, skipping"
            return
    cross_proj = qibuild_action.add_test_project("cross")
    toolchain_file = os.path.join(cross_proj.path, "toolchain.cmake")
    qibuild_action("configure", "cross",
                   "-G", cmake_generator,
                   "-DCMAKE_TOOLCHAIN_FILE=%s" % toolchain_file)
    qibuild_action("make", "cross",)
    qibuild_action("install", "cross",  tmpdir.strpath)

def test_running_tests_after_install(qibuild_action, tmpdir):
    testme = qibuild_action.add_test_project("testme")
    dest = tmpdir.join("dest")
    testme.configure()
    testme.build()
    testme.install(dest.strpath, components=["test"])
    qitest_json = dest.join("qitest.json")
    assert qitest_json.check(file=True)
    test_project = qitest.project.TestProject(qitest_json.strpath)
    test_runner = qibuild.test_runner.ProjectTestRunner(test_project)
    test_runner.patterns = ["ok"]
    test_runner.cwd = dest.strpath
    ok = test_runner.run()
    assert ok


def test_install_returns(qibuild_action, tmpdir):
    installme = qibuild_action.add_test_project("installme")
    dest = tmpdir.join("dest")
    installme.configure()
    installme.build()
    installed = installme.install(dest.strpath, components=["devel", "runtime"])
    if os.name == "nt":
        py_path = 'lib/py/foo.py'
    else:
        py_path = 'lib/python2.7/site-packages/py/foo.py'
    assert set(installed) == {'share/data_star/foo.dat',
                              'share/data_star/bar.dat',
                              'include/relative/foo/foo.h',
                              'include/relative/bar/bar.h',
                              'share/recurse/a_dir/b_dir/c_dir/d_file',
                              'share/recurse/a_dir/a_file',
                              'share/sub/bar.dat',
                              'share/qi/path.conf',
                              py_path}

def test_install_test_libs(qibuild_action, tmpdir):
    installme = qibuild_action.add_test_project("installme")
    dest = tmpdir.join("dest")
    installme.configure()
    installme.build()
    installme.install(dest.strpath, components=["runtime", "test"])

def test_json_merge_tests(qibuild_action, tmpdir):
    qibuild_action.add_test_project("testme")
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "--all")
    qibuild_action("make", "--all")
    dest = tmpdir.join("dest")
    qibuild_action("install", "--all", "--with-tests", dest.strpath)
    # tests from both hello and testme should be in the generated
    # json file
    qitest_json = dest.join("qitest.json")
    tests = qitest.conf.parse_tests(qitest_json.strpath)
    test_names = [x["name"] for x in tests]
    assert "zero_test" in test_names
    assert "ok" in test_names

def test_do_not_write_tests_twice(qibuild_action, tmpdir):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "--all")
    qibuild_action("make", "--all")
    dest = tmpdir.join("dest")
    qitest_json = dest.join("qitest.json")
    qibuild_action("install", "--all", "--with-tests", dest.strpath)
    tests = qitest.conf.parse_tests(qitest_json.strpath)
    first = len(tests)
    qibuild_action("install", "--all", "--with-tests", dest.strpath)
    tests = qitest.conf.parse_tests(qitest_json.strpath)
    second = len(tests)
    assert first == second

def test_do_not_generate_config_module_for_non_installed_targets(qibuild_action, tmpdir):
    qibuild_action.add_test_project("stagenoinstall")
    qibuild_action("configure", "--all")
    qibuild_action("make", "--all")
    dest = tmpdir.mkdir("dest")
    qibuild_action("install", "--all", dest.strpath)
    assert not dest.join("share", "cmake", "foo", "foo-config.cmake").check(file=True)

def test_no_packages(cd_to_tmpdir):
    # create a foo toolchain containing the world package
    qibuild_action = QiBuildAction()
    qitoolchain_action = QiToolchainAction()
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    qitoolchain_action("add-package", "-c", "foo", world_package)
    build_worktree.worktree.remove_project("world", from_disk=True)

    qibuild_action("configure", "-c", "foo", "hello")
    qibuild_action("make", "-c", "foo", "hello")
    dest = cd_to_tmpdir.mkdir("dest")
    qibuild_action("install", "--config", "foo", "--no-packages", "hello", dest.strpath)
    assert not dest.join("lib", "libworld.so").check(file=True)

def test_bin_sdk(qibuild_action, tmpdir):
    qibuild_action.add_test_project("binsdk")
    dest = tmpdir.mkdir("dest")
    qibuild_action("configure", "binsdk")
    qibuild_action("make", "binsdk")
    qibuild_action("install", "binsdk", dest.strpath)
    assert dest.join("lib", "libfoo.so").check(file=True)
    assert dest.join("lib", "libfoo.a").check(file=True)
    assert dest.join("include", "foo.h").check(file=True)
    assert dest.join("share", "cmake", "foo",
            "foo-config.cmake").check(file=True)

def test_with_tests_with_package(qibuild_action, qitoolchain_action, tmpdir):
    create_foo_toolchain_with_world_package(qibuild_action, qitoolchain_action)

    testme_proj = qibuild_action.add_test_project("testme")
    add_dep_to_world(testme_proj)

    dest = tmpdir.join("dest")

    qibuild_action("configure", "--config", "foo", "testme")
    qibuild_action("make", "--config", "foo", "testme")
    qibuild_action("install", "--config", "foo", "--with-tests",
                   "testme", dest.strpath)
    assert not dest.join("include", "world", "world.h").check(file=True)

def add_dep_to_world(project):
    qiproject_xml_path = os.path.join(project.path, "qiproject.xml")
    xml_tree = qisys.qixml.read(qiproject_xml_path).getroot()
    project.build_depends.add("world")
    project.run_depends.add("world")
    qibuild.deps.dump_deps_to_xml(project, xml_tree)
    qisys.qixml.write(xml_tree, qiproject_xml_path)

def test_install_path_conf(qibuild_action, tmpdir):
    qibuild_action.add_test_project("installme")
    qibuild_action("configure", "installme")
    qibuild_action("make", "installme")
    qibuild_action("install", "installme", tmpdir.strpath)
    assert tmpdir.join("share", "qi", "path.conf").check(file=True)

def test_meta(qibuild_action, tmpdir):
    dest = tmpdir.join("dest")
    top_proj = qibuild_action.add_test_project("meta/top")
    qibuild_action.add_test_project("meta/spam")
    qibuild_action.add_test_project("meta/eggs")
    qibuild_action("configure", "top")
    qibuild_action("make", "top")
    qibuild_action("install", "--runtime", "top", dest.strpath)
    assert qibuild.find.find_bin([dest.strpath], "spam")
    assert qibuild.find.find_bin([dest.strpath], "eggs")

    # Make sure no file has been created in the meta project sources:
    contents = qisys.sh.ls_r(top_proj.path)
    assert contents == ["qiproject.xml"]

def test_installing_tests(qibuild_action, tmpdir):
    dest = tmpdir.join("dest")
    qibuild_action.add_test_project("installme")
    qibuild_action("configure", "installme")
    qibuild_action("make", "installme")
    qibuild_action("install", "installme", dest.strpath)
    assert not qibuild.find.find_bin([dest.strpath], "test_foo", expect_one=False)
    qibuild_action("install", "--with-tests", "installme", dest.strpath)
    assert qibuild.find.find_bin([dest.strpath], "test_foo", expect_one=True)
