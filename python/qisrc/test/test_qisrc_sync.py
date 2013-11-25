import os

import py

import qisys.script
import qisys.sh
import qisrc.git
from qisrc.test.conftest import TestGitWorkTree, TestGit
from qibuild.test.conftest import TestBuildWorkTree
import qibuild.profile


def test_sync_clones_new_repos(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    # pylint: disable-msg=E1101
    cwd = py.path.local(os.getcwd())
    assert not cwd.join("foo").join("README").check(file=True)
    git_server.push_file("foo.git", "README", "This is foo\n")
    qisys.script.run_action("qisrc.actions.sync")
    assert cwd.join("foo").join("README").check(file=True)

def test_sync_skips_unconfigured_projects(qisrc_action, git_server, test_git):
    git_server.create_repo("foo.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    # pylint: disable-msg=E1101
    cwd = py.path.local(os.getcwd())
    new_proj = cwd.mkdir("new_proj")
    git = test_git(new_proj.strpath)
    git.initialize()
    git_worktree.add_git_project(new_proj.strpath)
    qisys.script.run_action("qisrc.actions.sync")

def test_clone_new_repos(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    git_server.create_repo("bar.git")
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    assert git_worktree.get_git_project("bar")


def test_configure_new_repos(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    qisrc_action("sync")
    git_server.create_repo("bar.git")
    qisrc_action("sync", "foo")  # Sync only foo, but expect to clone bar
    git_worktree = TestGitWorkTree()
    bar = git_worktree.get_git_project("bar")
    assert bar.default_remote


def test_creates_required_subdirs(qisrc_action, git_server):
    git_server.create_repo("foo/bar.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    assert git_worktree.get_git_project("foo/bar")


def test_uses_build_deps_by_default(qisrc_action, git_server):
    git_server.add_qibuild_test_project("world")
    git_server.add_qibuild_test_project("hello")
    git_server.create_repo("foo.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)

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
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    qibuild_xml = build_worktree.qibuild_xml
    foo_profile = qibuild.profile.parse_profiles(qibuild_xml)["foo"]
    assert foo_profile.name == "foo"
    assert foo_profile.cmake_flags == [("WITH_FOO", "ON")]

def test_sync_branch_devel(qisrc_action, git_server, test_git):
    # This tests the case where everything goes smoothly
    git_server.create_repo("foo.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
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
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
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
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
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
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    git_server.push_file("other", "other.txt", "change 2")
    qisrc_action("sync", "--group", "mygroup")

    git_worktree = TestGitWorkTree()
    other_proj = git_worktree.get_git_project("other")
    other_git = TestGit(other_proj.path)
    assert other_git.read_file("other.txt") == "change 1"

def test_incorrect_branch_still_fetches(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
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
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
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
