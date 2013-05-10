import os
import py

def test_clean_build_dir(qibuild_action):
    world_proj = qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")
    qibuild_action("clean", "world")
    assert os.path.exists(world_proj.build_directory)
    qibuild_action("clean", "-f", "world")
    assert not os.path.exists(world_proj.build_directory)

def test_only_clean_one_build_dir(qibuild_action, toolchains):
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    world_proj = build_worktree.get_build_project("world")
    toolchains.create("foo")
    qibuild_action("configure", "world")
    qibuild_action("configure", "-c", "foo", "world")

    qibuild_action("clean", "-f", "-c", "foo", "-a")
    assert os.path.exists(world_proj.build_directory)
    build_worktree.set_active_config("foo")
    assert not os.path.exists(world_proj.build_directory)

def test_cleaning_all_build_dirs(qibuild_action, toolchains):
    build_worktree = qibuild_action.build_worktree
    build_config = build_worktree.build_config
    world_proj = qibuild_action.add_test_project("world")
    toolchains.create("foo")
    qibuild_action("configure", "world")
    qibuild_action("configure", "-c", "foo", "world")
    qibuild_action("configure", "--release", "-c", "foo", "world")

    qibuild_action("clean", "-fz", "world")
    assert not os.path.exists(world_proj.build_directory)
    build_worktree.set_active_config("foo")
    assert not os.path.exists(world_proj.build_directory)
    build_config.build_type = "Release"
    assert not os.path.exists(world_proj.build_directory)


def test_clean_profiles(qibuild_action, toolchains, interact):
    build_worktree = qibuild_action.build_worktree
    build_worktree.configure_build_profile("a", [("A", "ON")])
    build_worktree.configure_build_profile("b", [("B", "ON")])
    toolchains.create("foo")
    world_proj = qibuild_action.add_test_project("world")
    # pylint: disable-msg=E1101
    world_path = py.path.local(world_proj.path)
    build_foo_a = world_path.ensure("build-foo-a", dir=True)
    build_foo_b = world_path.ensure("build-foo-b", dir=True)
    build_foo_a_b = world_path.ensure("build-foo-a-b", dir=True)
    build_foo_c = world_path.ensure("build-foo-c", dir=True)
    qibuild_action("clean", "-z", "--all", "--force")
    assert build_foo_a.check(dir=False)
    assert build_foo_b.check(dir=False)
    assert build_foo_a_b.check(dir=False)
    assert build_foo_c.check(dir=True)
    interact.answers = [True]
    qibuild_action("clean", "-x", "--all", "--force")
    assert build_foo_c.check(dir=False)
