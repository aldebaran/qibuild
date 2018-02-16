# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import os

import py
import pytest

import qisys.script
import qisys.sh
import qisrc.git
from qisrc.test.conftest import TestGitWorkTree, TestGit
from qibuild.test.conftest import TestBuildWorkTree
import qibuild.config
import qibuild.profile

# allow the existing foo/bar/baz names
# pylint: disable=blacklisted-name


def test_sync_clones_new_repos(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    # pylint: disable-msg=E1101
    cwd = py.path.local(os.getcwd())
    assert not cwd.join("foo").join("README").check(file=True)
    git_server.push_file("foo.git", "README", "This is foo\n")
    qisys.script.run_action("qisrc.actions.sync")
    assert cwd.join("foo").join("README").check(file=True)


def test_sync_skips_unconfigured_projects(qisrc_action, git_server, test_git):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    # pylint: disable-msg=E1101
    cwd = py.path.local(os.getcwd())
    new_proj = cwd.mkdir("new_proj")
    git = test_git(new_proj.strpath)
    git.initialize()
    git_worktree.add_git_project(new_proj.strpath)
    rc = qisrc_action("sync", retcode=True)
    assert rc != 0


def test_clone_new_repos(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_server.create_repo("bar.git")
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    assert git_worktree.get_git_project("bar")


def test_configure_new_repos(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("sync")
    git_server.create_repo("bar.git")
    qisrc_action("sync", "foo")  # Sync only foo, but expect to clone bar
    git_worktree = TestGitWorkTree()
    bar = git_worktree.get_git_project("bar")
    assert bar.default_remote


def test_creates_required_subdirs(qisrc_action, git_server):
    git_server.create_repo("foo/bar.git")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    assert git_worktree.get_git_project("foo/bar")


def test_uses_build_deps_by_default(qisrc_action, git_server):
    git_server.add_qibuild_test_project("world")
    git_server.add_qibuild_test_project("hello")
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)

    # Crete some changes in foo and world
    git_server.push_file("foo.git", "foo.txt", "unrelated changes")
    git_server.push_file("world.git", "world.txt", "dependency has been updated")

    # Sync hello
    qisrc_action.chdir("hello")
    qisrc_action("sync")
    qisrc_action.chdir(qisrc_action.root)
    git_worktree = TestGitWorkTree()

    # foo is not a dep, should not have changed:
    foo_proj = git_worktree.get_git_project("foo")
    foo_txt = os.path.join(foo_proj.path, "foo.txt")
    assert not os.path.exists(foo_txt)

    # World is a dep of hello:
    world_proj = git_worktree.get_git_project("world")
    world_txt = os.path.join(world_proj.path, "world.txt")
    assert os.path.exists(world_txt)


def test_sync_build_profiles(qisrc_action, git_server):
    git_server.add_build_profile("foo", [("WITH_FOO", "ON")])
    qisrc_action("init", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    qibuild.config.add_build_config("foo", profiles=["foo"])
    build_config.set_active_config("foo")
    cmake_args = build_config.cmake_args
    cmake_args = [x for x in cmake_args if "VIRTUALENV" not in x]
    assert cmake_args == ["-DCMAKE_BUILD_TYPE=Debug",
                          "-DWITH_FOO=ON"]
    git_server.add_build_profile("foo", [("WITH_FOO", "ON"), ("WITH_BAR", "ON")])
    qisrc_action("sync")
    cmake_args = build_config.cmake_args
    cmake_args = [x for x in cmake_args if "VIRTUALENV" not in x]
    assert cmake_args == ["-DCMAKE_BUILD_TYPE=Debug",
                          "-DWITH_FOO=ON", "-DWITH_BAR=ON"]


def test_sync_branch_devel(qisrc_action, git_server, test_git):
    # This tests the case where everything goes smoothly
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_server.push_file("foo.git", "foo.txt", "a super change")
    git_server.push_file("foo.git", "bar.txt", "a super bugfix")
    git_worktree = TestGitWorkTree()

    foo = git_worktree.get_git_project("foo")

    test_git = TestGit(foo.path)
    test_git.call("checkout", "-b", "devel")

    test_git.commit_file("developing.txt", "like a boss")
    git_server.push_file("foo.git", "foobar.txt", "some other change")
    git_server.push_file("foo.git", "bigchange.txt", "some huge change")

    qisrc_action("sync", "--rebase-devel")
    test_git.call("checkout", "master")
    # Check that master is fast-forwarded
    bigchange_txt = os.path.join(foo.path, "bigchange.txt")
    assert os.path.exists(bigchange_txt)

    # Check rebase is done smoothly
    test_git.call("checkout", "devel")
    test_git.call("rebase", "master")
    assert os.path.exists(bigchange_txt)
    developing_txt = os.path.join(foo.path, "developing.txt")
    assert os.path.exists(developing_txt)


def test_sync_branch_devel_unclean(qisrc_action, git_server, test_git):
    # Case where the worktree isn't clean

    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_server.push_file("foo.git", "foo.txt", "a super change")
    git_server.push_file("foo.git", "bar.txt", "a super bugfix")
    git_worktree = TestGitWorkTree()

    foo = git_worktree.get_git_project("foo")

    test_git = TestGit(foo.path)
    test_git.call("checkout", "-b", "devel")

    test_git.commit_file("developing.txt", "like a boss")
    git_server.push_file("foo.git", "foobar.txt", "some other change")

    wip_txt = os.path.join(foo.path, "wip.txt")
    open(wip_txt, 'w').close()

    qisys.script.run_action("qisrc.actions.sync", ["--rebase-devel"])
    # Master has been fast-forwarded and I haven't lost my WIP
    assert os.path.exists(wip_txt)


def test_sync_branch_devel_no_ff(qisrc_action, git_server, test_git):
    # Case where master can't be fast-forwarded, does nothing except warning

    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_server.push_file("foo.git", "foo.txt", "a super change")
    git_worktree = TestGitWorkTree()

    foo = git_worktree.get_git_project("foo")

    test_git = TestGit(foo.path)
    test_git.commit_file("foo.git", "div.txt", "diverging from master")
    master_sha1 = test_git.get_ref_sha1("refs/heads/master")
    test_git.call("checkout", "-b", "devel")

    test_git.commit_file("developing.txt", "like a boss")
    git_server.push_file("foo.git", "foobar.txt", "some other change")

    qisrc_action("sync", "--rebase-devel")
    # Master HEAD is untouched
    assert test_git.get_ref_sha1("refs/heads/master") == master_sha1


def test_sync_dash_g(qisrc_action, git_server):
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("other")
    git_server.push_file("other", "other.txt", "change 1")
    qisrc_action("init", git_server.manifest_url)
    git_server.push_file("other", "other.txt", "change 2")
    qisrc_action("sync", "--group", "mygroup")

    git_worktree = TestGitWorkTree()
    other_proj = git_worktree.get_git_project("other")
    other_git = TestGit(other_proj.path)
    assert other_git.read_file("other.txt") == "change 1"


def test_incorrect_branch_still_fetches(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    foo = git_worktree.get_git_project("foo")
    test_git = TestGit(foo.path)
    test_git.checkout("-b", "wip")
    git_server.push_file("foo.git", "foo.txt", "some change")
    previous_sha1 = test_git.get_ref_sha1("refs/remotes/origin/master")
    foo.sync()
    new_sha1 = test_git.get_ref_sha1("refs/remotes/origin/master")
    assert previous_sha1 != new_sha1


def test_keeps_staged_changes(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    foo = git_worktree.get_git_project("foo")
    test_git = TestGit(foo.path)
    staged_file = os.path.join(foo.path, "staged")
    with open(staged_file, "w") as f:
        f.write("I'm going to stage stuff")
    test_git.add(staged_file)
    foo.sync()
    assert os.path.exists(staged_file)


def test_new_project_under_gitorious(git_worktree, git_server):
    git_server.create_repo("foo", review=False)
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest(manifest_url)
    foo = git_worktree.get_git_project("foo")
    git_server.use_gitorious("foo")
    worktree_syncer.sync()
    foo = git_worktree.get_git_project("foo")
    assert len(foo.remotes) == 1
    assert foo.default_remote.name == "gitorious"


def test_removing_forked_project(qisrc_action, git_server):
    git_server.create_repo("booz")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("booz", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_worktree = TestGitWorkTree()
    booz_proj = git_worktree.get_git_project("booz")
    git = qisrc.git.Git(booz_proj.path)
    assert git.get_current_branch() == "devel"
    git_server.change_branch("booz", "master")
    qisrc_action("sync", "-a", retcode=True)
    qisrc_action("checkout", "devel")
    assert git.get_current_branch() == "master"


def test_sync_reset(qisrc_action, git_server):
    git_server.create_repo("bar")
    git_server.create_repo("baz")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    bar_proj = git_worktree.get_git_project("bar")
    baz_proj = git_worktree.get_git_project("baz")
    bar_git = TestGit(bar_proj.path)
    baz_git = TestGit(baz_proj.path)
    bar_git.checkout("-B", "devel")
    baz_git.commit_file("unrelated.txt", "unrelated\n")
    git_server.push_file("bar", "bar.txt", "this is bar\n")
    qisrc_action("sync", "--reset")
    assert bar_git.get_current_branch() == "master"
    assert bar_git.read_file("bar.txt") == "this is bar\n"
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        baz_git.read_file("unrelated.txt")


def test_retcode_when_skipping(qisrc_action, git_server):
    git_server.create_repo("bar")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    bar_proj = git_worktree.get_git_project("bar")
    git = TestGit(bar_proj.path)
    git.checkout("-b", "devel")
    rc = qisrc_action("sync", retcode=True)
    assert rc != 0


def test_do_not_sync_when_clone_fails(qisrc_action, git_server, record_messages):
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    git_server.create_repo("baz.git")
    git_server.srv.join("baz.git").remove()
    rc = qisrc_action("sync", retcode=True)
    assert rc != 0
    assert not record_messages.find("Success")


def test_changing_branch_of_repo_under_code_review(qisrc_action, git_server,
                                                   record_messages):
    git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_server.change_branch("foo.git", "devel")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.checkout("-b", "devel")
    record_messages.reset()
    qisrc_action("sync")
    assert record_messages.find("default branch changed")
    assert not record_messages.find("now using code review")


def test_using_code_review(qisrc_action, git_server, record_messages):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_server.use_review("foo.git")
    record_messages.reset()
    qisrc_action("sync")
    assert record_messages.find("now using code review")


def test_no_manifest(qisrc_action):
    error = qisrc_action("sync", raises=True)
    assert "No manifest" in error


def test_dash_reset(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    git_server.change_branch("foo.git", "devel")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("sync", "--reset")


def test_removing_group_user_removes_group_by_hand(qisrc_action, git_server,
                                                   record_messages):
    git_server.create_group("foo", ["a.git"])
    git_server.create_group("bar", ["b.git"])
    qisrc_action("init", git_server.manifest_url,
                 "--group", "foo",
                 "--group", "bar")
    git_server.remove_group("foo")
    qisrc_action("sync")
    assert record_messages.find("Group foo not found in the manifest")
    record_messages.reset()
    qisrc_action("rm-group", "foo")
    qisrc_action("sync")
    assert not record_messages.find("WARN")


def test_removing_group_keep_warning_user(qisrc_action, git_server,
                                          record_messages):
    git_server.create_group("foo", ["a.git"])
    git_server.create_group("bar", ["b.git"])
    qisrc_action("init", git_server.manifest_url,
                 "--group", "foo",
                 "--group", "bar")
    git_server.remove_group("foo")
    qisrc_action("sync")
    assert record_messages.find("Group foo not found in the manifest")
    record_messages.reset()
    qisrc_action("sync")
    assert record_messages.find("Group foo not found in the manifest")


def _test_switching_to_fixed_ref_happy(qisrc_action, git_server, record_messages, tag_ref_to_test, branch_ref_to_test):
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    git_server.push_branch("foo.git", "feature/b")
    git_server.push_file("foo.git", "c.txt", "c")
    qisrc_action("init", git_server.manifest_url)

    # Check for fixed_ref tag
    git_server.set_fixed_ref("foo.git", tag_ref_to_test)
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.1")
    assert sha1 == expected
    # qisrc.reset.clever_reset_ref should tell where is the HEAD after reset
    record_messages.reset()
    qisrc_action("sync")
    assert record_messages.find("HEAD is now at")
    assert record_messages.find("Add a.txt")
    _, status_output = git.status(raises=False)
    assert "HEAD" in status_output
    assert "detached" in status_output

    # If branch ref name is local, makesure it exists on local copy, then go back to master
    if branch_ref_to_test == "feature/b":
        git.checkout("feature/b", raises=False)
        git.checkout("master", raises=False)

    # Check for fixed_ref branch
    git_server.set_fixed_ref("foo.git", branch_ref_to_test)
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/remotes/origin/feature/b")
    assert sha1 == expected
    # qisrc.reset.clever_reset_ref should tell where is the HEAD after reset
    record_messages.reset()
    qisrc_action("sync")
    assert record_messages.find("HEAD is now at")
    assert record_messages.find("Add b.txt")
    _, status_output = git.status(raises=False)

    # FIXME: when using ref long name branch (refs/xxx), if we come from a tag, we stay in a detached head,
    # and we should be in an attached head state to be consistent with the ref short name branc behaviour
    # That's not an issue for now as users reference short name in manifest, but it will be cleaner to be consistent...
    if not branch_ref_to_test.startswith("refs/"):
        assert "HEAD" not in status_output
        assert "detached" not in status_output
    else:
        # Remove these assert when dealing with behaviour consistency mentionned above
        assert "HEAD" in status_output
        assert "detached" in status_output


def test_switching_to_fixed_ref_short_name_happy(qisrc_action, git_server, record_messages):
    _test_switching_to_fixed_ref_happy(qisrc_action, git_server, record_messages,
                                       "v0.1", "feature/b")


def test_switching_to_fixed_ref_remote_long_name_happy(qisrc_action, git_server, record_messages):
    _test_switching_to_fixed_ref_happy(qisrc_action, git_server, record_messages,
                                       "refs/tags/v0.1", "refs/heads/feature/b")


def test_switching_to_fixed_ref_local_long_name_happy(qisrc_action, git_server, record_messages):
    # Need to configure a remote origin
    _test_switching_to_fixed_ref_happy(qisrc_action, git_server, record_messages,
                                       "refs/tags/v0.1", "refs/remotes/origin/feature/b")


def test_fixed_ref_local_changes(qisrc_action, git_server, record_messages):
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "a.txt", "a")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.write_file("a.txt", "unstaged changes")
    git_server.push_tag("foo.git", "v.01")
    record_messages.reset()
    rc = qisrc_action("sync", retcode=True)
    assert rc != 0
    assert record_messages.find("unstaged changes")


def test_fixed_ref_no_such_ref(qisrc_action, git_server, record_messages):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_server.set_fixed_ref("foo.git", "v0.1")
    rc = qisrc_action("sync", retcode=True)
    assert rc != 0
    assert record_messages.find("Could not parse v0.1 as a valid ref")


def test_switching_to_new_fixed_ref(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    git_server.push_tag("foo.git", "v0.2")
    git_server.push_file("foo.git", "c.txt", "c")
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("init", git_server.manifest_url)
    git_server.set_fixed_ref("foo.git", "v0.2")
    qisrc_action("sync", retcode=True)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.2")
    assert sha1 == expected


def test_switching_to_new_fixed_ref_local_changes(qisrc_action, git_server, record_messages):
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    git_server.push_tag("foo.git", "v0.2")
    git_server.push_file("foo.git", "c.txt", "c")
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.write_file("a.txt", "unstaged changes")
    git_server.set_fixed_ref("foo.git", "v0.2")
    record_messages.reset()
    rc = qisrc_action("sync", retcode=True)
    # ERROR message must be displayed to warn user
    assert rc != 0
    assert record_messages.find("unstaged changes")
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.1")
    # git repo unchanged
    assert sha1 == expected
    git.call("reset", "--hard")
    rc = qisrc_action("sync", retcode=True)
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.2")
    # if modification is revert sync must be successful
    assert rc != 0
    assert sha1 == expected


def test_switching_from_fixed_ref_to_branch(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    qisrc_action("init", git_server.manifest_url)
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.1")
    assert sha1 == expected
    git_server.set_branch("foo.git", "master")
    qisrc_action("sync")
    assert git.get_current_branch() == "master"


def test_switching_from_fixed_ref_to_branch_local_changes(qisrc_action, git_server, record_messages):
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    git_server.push_tag("foo.git", "v0.2")
    git_server.push_file("foo.git", "c.txt", "c")
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.write_file("a.txt", "unstaged changes")
    git_server.set_branch("foo.git", "master")
    record_messages.reset()
    rc = qisrc_action("sync", retcode=True)
    # ERROR message must be displayed to warn user
    assert rc != 0
    assert record_messages.find("unstaged changes")
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.1")
    # git repo unchanged
    assert sha1 == expected
    git.call("reset", "--hard")
    qisrc_action("sync", retcode=True)
    # if modification is revert sync must be successful
    assert git.get_current_branch() == "master"
