## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import tempfile
import unittest
import pytest

import qisrc.git
import qisys.sh

from qisys.test.conftest import worktree

def read_readme(src):
    """ Returns the contents for the README file
    Useful to check on what branch we are

    """
    readme = os.path.join(src, "README")
    with open(readme, "r") as fp:
        return fp.read()

def write_readme(src, text, append=False):
    """ Write some text in the README.
    Useful to create un-staged changes, conflicts
    and whatnot

    """
    readme = os.path.join(src, "README")
    if append:
        mode = "a"
    else:
        mode = "w"
    with open(readme, mode) as fp:
        return fp.write(text)

def create_git_repo(tmp, path, with_release_branch=False):
    """ Create a empty git repository, which just
    what is enough so that it is possible to clone it

    Return a valid git url.
    """
    tmp_srv = os.path.join(tmp, "srv", path + ".git")
    qisys.sh.mkdir(tmp_srv, recursive=True)
    srv_git = qisrc.git.Git(tmp_srv)
    srv_git.call("init", "--bare")

    tmp_src = os.path.join(tmp, "src", path)
    qisys.sh.mkdir(tmp_src, recursive=True)
    write_readme(tmp_src, path + "\n")
    git = qisrc.git.Git(tmp_src)
    git.call("init")
    git.call("add", ".")
    git.call("commit", "-m", "intial commit")
    git.call("push", tmp_srv, "master:master")

    if not with_release_branch:
        return tmp_srv

    git.checkout("-b", "release-1.12")
    write_readme(tmp_src, "%s on release-1.12\n" % path)
    git.call("add", "README")
    git.call("commit", "-m", "update README for 1.12")
    git.call("push", tmp_srv, "release-1.12:release-1.12")
    return tmp_srv


def create_git_repo_with_submodules(tmp):
    """ Return a foo.git url matching a repository
    contaning a submodule in bar/

    """
    bar_url = create_git_repo(tmp, "bar")
    foo_url = create_git_repo(tmp, "foo")
    foo_src = os.path.join(tmp, "src", "foo")
    foo_git = qisrc.git.Git(foo_src)
    foo_git.call("submodule", "add", bar_url, "bar")
    foo_git.call("commit", "-m", "add bar submodule")
    foo_git.call("push", foo_url, "master:master")
    return foo_url

def create_broken_submodules(tmp):
    """ Return an URL where there will be a registered submodule,
    but no .gitmodules (it happens)

    """
    foo_url = create_git_repo_with_submodules(tmp)
    foo_src = os.path.join(tmp, "src", "foo")
    foo_git = qisrc.git.Git(foo_src)
    foo_git.call("rm", ".gitmodules")
    foo_git.call("commit", "-m", "trying to remove submodules, but in a bad way")
    foo_git.call("push", foo_url, "master:master")

def push_file(tmp, git_path, filename, contents, branch="master"):
    """ Push a file to the given url. Assumes the repository
    has been created with :py:func:`create_git_repo` with the same
    path

    """
    tmp_src = os.path.join(tmp, "src", git_path)
    tmp_srv = os.path.join(tmp, "srv", git_path + ".git")
    git = qisrc.git.Git(tmp_src)
    if branch in git.get_local_branches():
        git.checkout("-f", branch)
    else:
        git.checkout("-b", branch)
    dirname = os.path.dirname(filename)
    qisys.sh.mkdir(os.path.join(tmp_src, dirname), recursive=True)
    with open(os.path.join(tmp_src, filename), "w") as fp:
        fp.write(contents)
    git.add(filename)
    git.commit("-m", "added %s" % filename)
    git.push(tmp_srv, "%s:%s" % (branch, branch))

def push_readme_v2(tmp, path, branch):
    """ Push version 2 of the readme to the git repo in the given branch

    """
    push_file(tmp, path, "README", "%s v2 on %s\n" % (path, branch), branch=branch)


# pylint: disable-msg=E1101
@pytest.mark.slow
class GitTestCase(unittest.TestCase):
    def setUp(self):
        qisys.command.CONFIG["quiet"] = True
        self.tmp = tempfile.mkdtemp(prefix="test-qisrc-sync")

    def tearDown(self):
        qisys.command.CONFIG["quiet"] = True
        qisys.sh.rm(self.tmp)

    def test_set_remote(self):
        bar_url = create_git_repo(self.tmp, "bar", with_release_branch=True)
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url,  "-o", "foo")
        # Must work:
        git.pull()
        git.set_remote("origin", bar_url)
        # Must NOT work:
        out, err_ = git.pull("origin", raises=False)
        self.assertFalse(out == 0)
        # Must work
        git.set_tracking_branch("master", "origin")
        git.pull()
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar\n")
        git.set_tracking_branch("stable", "origin", remote_branch="release-1.12")
        git.checkout("stable")
        git.pull()
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar on release-1.12\n")

    def test_get_current_branch(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)
        self.assertEqual(git.get_current_branch(), "master")
        push_readme_v2(self.tmp, "bar", "master")
        git.pull()
        self.assertEqual(git.get_current_branch(), "master")
        git.checkout("-f", "HEAD~1")
        self.assertEqual(git.get_current_branch(), None)


# pylint: disable-msg=E1101
@pytest.mark.slow
class GitUpdateBranchTestCase(unittest.TestCase):
    def setUp(self):
        qisys.command.CONFIG["quiet"] = True
        self.tmp = tempfile.mkdtemp(prefix="test-qisrc-sync")

    def tearDown(self):
        qisys.command.CONFIG["quiet"] = True
        qisys.sh.rm(self.tmp)

    def test_simple(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)
        # Should be a noop
        git.update_branch("master", "origin")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar\n")

        # Push a new commit
        push_readme_v2(self.tmp, "bar", "master")

        # Update, check that branch is up to date
        git.update_branch("master", "origin")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar v2 on master\n")

    def test_wrong_branch(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)
        git.update_branch("master", "origin")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar\n")

        # Checkout a 'next' branch
        git.checkout("-b", "next")
        with open(os.path.join(bar_src, "README"), "w") as fp:
            fp.write("bar on next\n")
        git.commit("-a", "-m", "README next")

        # Push a new commit
        push_readme_v2(self.tmp, "bar", "master")

        # Update, check that master is up to date
        err = git.update_branch("master", "origin")
        self.assertFalse(err)
        git.checkout("master")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar v2 on master\n")

    def test_conflict(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Create conflicting changes
        write_readme(bar_src, "conflicting changes\n", append=True)
        git.commit("-a", "-m", "conflicting changes")
        push_readme_v2(self.tmp, "bar", "master")

        # Updating branch should fail
        err = git.update_branch("master", "origin")
        self.assertTrue(err)
        self.assertTrue("Merge conflict in README" in err, err)

        # But we should be back at our previous commit
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar\nconflicting changes\n")

        self.assertEqual(git.get_current_branch(), "master")
        rebase_apply = os.path.join(git.repo, ".git", "rebase_apply")
        self.assertFalse(os.path.exists(rebase_apply))

    def test_untracked_files(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Create untracked, non-conflicting changes
        a_file = os.path.join(bar_src, "a_file")
        with open(a_file, "w") as fp:
            fp.write("a_file\n")
        push_readme_v2(self.tmp, "bar", "master")

        # Update branch, untracked files should still be here
        err = git.update_branch("master", "origin")
        self.assertFalse(err)

        self.assertTrue(os.path.exists(a_file))
        with open(a_file, "r") as fp:
            contents = fp.read()
        self.assertEqual(contents, "a_file\n")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar v2 on master\n")

    def test_untracked_would_be_overwritten(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Create untracked, conflicting changes
        a_file = os.path.join(bar_src, "a_file")
        with open(a_file, "w") as fp:
            fp.write("a_file\n")

        upstream_src = os.path.join(self.tmp, "src", "bar")
        upstream_file = os.path.join(upstream_src, "a_file")
        with open(upstream_file, "w") as fp:
            fp.write("upstream file\n")
        upstream_git = qisrc.git.Git(upstream_src)
        upstream_git.call("add", "a_file")
        upstream_git.call("commit", "-m", "Add a file")
        upstream_git.call("push", bar_url, "master:master")

        err = git.update_branch("master", "origin")
        self.assertTrue(err)
        self.assertTrue("untracked working tree files" in err)
        self.assertEqual(git.get_current_branch(), "master")

    def test_unstaged_changes_conflict(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Create unstaged, conflicting changes
        readme = os.path.join(bar_src, "README")
        with open(readme, "a") as fp:
            fp.write("Unstaged changes\n")
        push_readme_v2(self.tmp, "bar", "master")

        err = git.update_branch("master", "origin")
        self.assertTrue(err)
        self.assertTrue("Merge conflict in README" in err)
        self.assertTrue("Stashing back changes failed" in err)
        self.assertTrue(git.get_current_branch(), "master")
        rebase_apply = os.path.join(git.repo, ".git", "rebase_apply")
        self.assertFalse(os.path.exists(rebase_apply))
        readme = read_readme(bar_src)
        self.assertTrue(readme, "Unstaged changes\n")

    def test_unstaged_changes_no_conflict(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Create unstaged, non-conflicting changes
        readme = os.path.join(bar_src, "README")
        with open(readme, "w") as fp:
            fp.write("Unstaged changes\n")

        upstream_src = os.path.join(self.tmp, "src", "bar")
        upstream_file = os.path.join(upstream_src, "a_file")
        with open(upstream_file, "w") as fp:
            fp.write("upstream file\n")
        upstream_git = qisrc.git.Git(upstream_src)
        upstream_git.call("add", "a_file")
        upstream_git.call("commit", "-m", "Add a file")
        upstream_git.call("push", bar_url, "master:master")

        err = git.update_branch("master", "origin")
        self.assertFalse(err)

        # Check that upstream file is here
        a_file = os.path.join(bar_src, "a_file")
        self.assertTrue(os.path.exists(a_file))

        # Check that unstaged changes are here:
        readme = read_readme(bar_src)
        self.assertEqual(readme, "Unstaged changes\n")

        self.assertTrue(git.get_current_branch(), "master")
        rebase_apply = os.path.join(git.repo, ".git", "rebase_apply")
        self.assertFalse(os.path.exists(rebase_apply))


    def test_wrong_branch_unstaged(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Checkout a 'next' branch with unstaged changes
        git.checkout("-b", "next")
        write_readme(bar_src, "bar on next\n")
        push_readme_v2(self.tmp, "bar", "master")

        err = git.update_branch("master", "origin")
        self.assertFalse(err)

        # Check we are still on next with our
        # unstaged changes back
        self.assertEqual(git.get_current_branch(), "next")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar on next\n")

        # Check that master is up to date
        git.checkout("-f", "master")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar v2 on master\n")

    def test_wrong_branch_with_conflicts(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qisys.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Create conflicting changes
        write_readme(bar_src, "conflicting changes\n", append=True)
        git.commit("-a", "-m", "conflicting changes")
        push_readme_v2(self.tmp, "bar", "master")

        # Checkout an other branch
        git.checkout("-b", "next")

        # Try to update master while being on an other branch:
        err = git.update_branch("master", "origin")
        self.assertTrue(err)
        self.assertTrue("Merge is not fast-forward" in err)


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_git_get_local_branches(tmpdir):
    tmpdir = tmpdir.strpath
    git = qisrc.git.Git(tmpdir)
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        git.get_local_branches()
    write_readme(tmpdir, "readme\n")
    git.call("init")
    git.call("add", ".")
    git.commit("-m", "initial commit")
    assert git.get_local_branches() == ["master"]
    git.checkout("-b", "devel")
    assert git.get_local_branches() == ["devel", "master"]


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_set_tracking_branch(tmpdir):
    tmpdir = tmpdir.strpath
    bar_url = create_git_repo(tmpdir, "bar")
    work = os.path.join(tmpdir, "work")
    bar_src = os.path.join(work, "bar")
    git = qisrc.git.Git(bar_src)
    git.clone(bar_url)

    push_file(tmpdir, "bar", "README", "README on release",  branch="release")
    push_file(tmpdir, "bar", "README", "README on master", branch="master")
    git.update_branch("master", "origin")

    git.set_tracking_branch("release", "origin")
    err = git.update_branch("release", "origin")
    assert not err

    # This should work out of the box
    git.pull()
    git.checkout("release")
    git.pull()


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_submodules(tmpdir):
    foo_url = create_git_repo_with_submodules(tmpdir.strpath)
    work = tmpdir.mkdir("work")
    foo = work.mkdir("foo")
    git = qisrc.git.Git(foo.strpath)
    git.clone(foo_url)
    bar = foo.join("bar")
    assert qisrc.git.is_submodule(bar.strpath)
    assert not qisrc.git.is_submodule(foo.strpath)
    git.update_submodules()
    assert qisrc.git.is_submodule(bar.strpath)

def test_create_in_git_dir(tmpdir):
    a_git = tmpdir.mkdir("a_git_project")
    a_manifest = tmpdir.join("a_manifest.xml")
    a_manifest.write("<manifest />")
    git = qisrc.git.Git(a_git.strpath)
    git.init()
    work = a_git.mkdir("work")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.worktree.create(work.strpath)
    assert "inside a git project" in e.value.message

def test_get_repo_root(tmpdir):
    a_nogit = tmpdir.mkdir("a_nogit_project")
    a_git = tmpdir.mkdir("a_git_project")
    git = qisrc.git.Git(a_git.strpath)
    git.init()
    work = a_git.mkdir("work")

    assert qisrc.git.get_repo_root(a_nogit.strpath) == None
    assert qisrc.git.get_repo_root(a_git.strpath)   == a_git.strpath
    assert qisrc.git.get_repo_root(work.strpath)    == a_git.strpath
    assert qisrc.git.get_repo_root(os.path.join(tmpdir.strpath, "pouet")) == None

def test_is_ff(tmpdir):
    a_git = tmpdir.mkdir("a_git_project")
    a_src = a_git.strpath

    git = qisrc.git.Git(a_src)
    git.init()
    write_readme(a_src, "readme\n")
    git.add(".")
    git.commit("-m", "initial commit")
    git.call("branch", "A")

    write_readme(a_src, "readme2\n")
    git.add(".")
    git.commit("-m", "second commit")
    git.call("branch", "B")

    (ret, out) = git.call("show-ref", "--verify", "refs/heads/A", raises=False)
    A_sha1 = out.split()[0]
    (ret, out) = git.call("show-ref", "--verify", "refs/heads/B", raises=False)
    B_sha1 = out.split()[0]

    class Status:
        pass
    status = Status()
    status.mess = ""
    assert qisrc.git.is_ff(git, status, A_sha1, B_sha1) == True
    assert qisrc.git.is_ff(git, status, B_sha1, A_sha1) == False
    assert qisrc.git.is_ff(git, status, A_sha1, A_sha1) == True

def test_get_ref_sha1(tmpdir):
    a_git = tmpdir.mkdir("a_git_project")
    git = qisrc.git.Git(a_git.strpath)

    assert git.is_valid() == False

    git.init()
    assert git.is_valid() == True

def test_add_git_project(tmpdir, worktree):
    worktree.add_project("foo")
    foo_dir = tmpdir.join("work").mkdir("foo").strpath
    git = qisrc.git.Git(foo_dir).init()
    wt = qisys.worktree.open_worktree(tmpdir.join("work").strpath)
    assert len(qisrc.git.get_git_projects(wt)) == 1
    assert worktree.get_project("foo").src == "foo"
