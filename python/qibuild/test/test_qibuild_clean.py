## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import platform
import py

import qisys.sh
import qibuild.config
import qibuild.profile

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


def test_using_build_prefix(qibuild_action, tmpdir):
    mybuild = tmpdir.join("mybuild")
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world", "--build-prefix", mybuild.strpath)
    build_dir = mybuild.join("world",
                             "build-sys-%s-%s" % (platform.system().lower(),
                                                platform.machine().lower()))
    assert build_dir.check(dir=True)
    qibuild_action("clean", "world", "-z", "--force",
                   "--build-prefix", mybuild.strpath)
    assert build_dir.check(dir=False)
