## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import platform
import py

import qisys.sh
import qibuild.config
import qibuild.profile

from qibuild.test.conftest import TestBuildWorkTree

def test_clean_build_dir(qibuild_action):
    world_proj = qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")
    qibuild_action("clean", "world")
    assert os.path.exists(world_proj.build_directory)
    qibuild_action("clean", "-f", "world")
    assert not os.path.exists(world_proj.build_directory)

def test_only_clean_one_build_dir(qibuild_action):
    qibuild.config.add_build_config("foo")
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    world_proj = build_worktree.get_build_project("world")
    qibuild_action("configure", "world")
    qibuild_action("configure", "-c", "foo", "world")

    qibuild_action("clean", "-f", "-c", "foo", "-a")
    assert os.path.exists(world_proj.build_directory)
    build_worktree.set_active_config("foo")
    assert not os.path.exists(world_proj.build_directory)

def test_cleaning_all_build_dirs(qibuild_action):
    qibuild.config.add_build_config("foo")
    build_worktree = qibuild_action.build_worktree
    build_config = build_worktree.build_config
    world_proj = qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")
    qibuild_action("configure", "-c", "foo", "world")
    qibuild_action("configure", "--release", "-c", "foo", "world")

    qibuild_action("clean", "-fz", "world")
    assert not os.path.exists(world_proj.build_directory)
    build_worktree.set_active_config("foo")
    assert not os.path.exists(world_proj.build_directory)
    build_config.build_type = "Release"
    assert not os.path.exists(world_proj.build_directory)

def test_cleaning_unknown_configs(qibuild_action, toolchains, interact):
    qibuild.config.add_build_config("a")
    qibuild.config.add_build_config("b")
    world_proj = qibuild_action.add_test_project("world")
    # pylint: disable-msg=E1101
    world_path = py.path.local(world_proj.path)
    build_a = world_path.ensure("build-a", dir=True)
    build_b = world_path.ensure("build-b", dir=True)
    build_c = world_path.ensure("build-c", dir=True)
    qibuild_action("clean", "-z", "--all", "--force")
    assert build_a.check(dir=False)
    assert build_b.check(dir=False)
    assert build_c.check(dir=True)
    interact.answers = [True]
    qibuild_action("clean", "-x", "--all", "--force")
    assert build_c.check(dir=False)

def test_using_build_prefix_from_cli(qibuild_action, tmpdir):
    mybuild = tmpdir.join("mybuild")
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world", "--build-prefix", mybuild.strpath)
    build_dir = mybuild.join("build-sys-%s-%s" % (platform.system().lower(),
                                                platform.machine().lower()),
                            "world")
    assert build_dir.check(dir=True)
    qibuild_action("clean", "world", "-z", "--force",
                   "--build-prefix", mybuild.strpath)
    assert build_dir.check(dir=False)

def test_using_build_prefix_from_config_deps_already_cleaned(tmpdir, monkeypatch):
    myprefix = "../prefix"
    work = tmpdir.mkdir("work")
    dot_qi = work.mkdir(".qi")
    qibuild_xml = dot_qi.join("qibuild.xml")
    to_write = """\
<qibuild version="1">
  <build prefix="%s" />
</qibuild>
"""
    qibuild_xml.write(to_write % myprefix)
    worktree = qisys.worktree.WorkTree(work.strpath)
    build_worktree = TestBuildWorkTree(worktree)
    bar_proj = build_worktree.create_project("bar")
    foo_proj = build_worktree.create_project("foo", build_depends=["bar"])
    foo_proj.configure()
    build_dir = foo_proj.build_directory
    assert os.path.exists(build_dir)
    monkeypatch.chdir(foo_proj.path)
    qisys.script.run_action("qibuild.actions.clean", ["--force", "-z"])
    assert not os.path.exists(build_dir)
