## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qisys.archive
import qisys.qixml
import qisrc.license
import qisrc.git
import qibuild.config
import qibuild.find
import qitoolchain.qipackage

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

import pytest

def test_simple(qibuild_action):
    qibuild_action.add_test_project("world")
    world_archive = qibuild_action("package", "world")
    assert os.path.exists(world_archive)
    qipackage = qitoolchain.qipackage.from_archive(world_archive)
    assert qipackage.name == "world"

def test_building_in_release(qibuild_action):
    qibuild_action.add_test_project("world")
    qibuild_action("package", "world", "--release")

def test_using_toolchain(cd_to_tmpdir):
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

    # this should now fail (no world-config.cmake found)
    qibuild_action("configure", "hello", raises=True)

    # but this should pass:
    qibuild_action("configure", "-c", "foo", "hello")

def test_preserve_license(qibuild_action, qitoolchain_action):
    world_proj = qibuild_action.add_test_project("world")
    qisrc.license.write_license(world_proj.qiproject_xml, "BSD")
    world_package = qibuild_action("package", "world")
    extracted = qitoolchain_action("extract-package", world_package)
    package_xml = os.path.join(extracted, "package.xml")
    license = qisrc.license.read_license(package_xml)
    assert license == "BSD"

def test_standalone(qibuild_action, tmpdir):
    world_proj = qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    hello_archive = qibuild_action("package", "hello", "--standalone")

    # Make sure bin/hello can run after extracting the standalone
    # package
    dest = tmpdir.join("dest")
    extracted = qisys.archive.extract(hello_archive, dest.strpath)
    hello_bin = qibuild.find.find_bin([extracted], "hello")
    qisys.command.call([hello_bin])

def test_standalone_version_from_cmd_line(qibuild_action, toolchains, tmpdir):
    toolchains.create("linux64")
    qibuild.config.add_build_config("linux64", toolchain="linux64")
    world_proj = qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    hello_archive = qibuild_action("package", "--config", "linux64",
                                   "--standalone", "--version", "0.42",
                                   "hello")
    expected_name = "hello-0.42-linux64"
    assert os.path.basename(hello_archive) == expected_name + ".zip"
    dest = tmpdir.join("dest")
    extracted = qisys.archive.extract(hello_archive, dest.strpath)
    package_xml = os.path.join(extracted, "package.xml")
    tree = qisys.qixml.read(package_xml)
    assert tree.getroot().get("version") == "0.42"

# pylint: disable-msg=E1101
@pytest.mark.skipif(not qisys.command.find_program("dump_syms"),
                    reason="dump_syms not found")
def test_standalone_breakpad(qibuild_action, tmpdir):
    world_proj = qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    hello_archive, hello_symbols = qibuild_action("package", "hello", "--standalone",
                                                  "--breakpad")
    assert os.path.exists(hello_symbols)


def test_setting_version_from_cmdline(qibuild_action):
    qibuild_action.add_test_project("world")
    world_package = qibuild_action("package", "world", "--version", "0.42")
    basename = os.path.basename(world_package)
    assert "0.42" in basename


def test_package_project_not_in_manifest(build_worktree, qibuild_action):
    this_dir = os.path.dirname(__file__)
    src_path = os.path.join(this_dir, "projects", "world")
    dest_path = os.path.join(build_worktree.root, "world")
    qisys.sh.copy_git_src(src_path, dest_path)
    # Init the project so that it's considered a git project not in manifest
    # (as if it was cloned manually in a worktree)
    git = qisrc.git.Git(dest_path)
    git.init()
    git.commit("--allow-empty", "-m", "init")
    qibuild_action.chdir(dest_path)
    qibuild_action("package")
