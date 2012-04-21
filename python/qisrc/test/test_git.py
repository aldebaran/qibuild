## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import tempfile
import unittest

import qisrc.git
import qibuild.sh

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

    Rerturn a valid git url.
    """
    tmp_srv = os.path.join(tmp, "srv", path + ".git")
    qibuild.sh.mkdir(tmp_srv, recursive=True)
    srv_git = qisrc.git.Git(tmp_srv)
    srv_git.call("init", "--bare")

    tmp_src = os.path.join(tmp, "src", path)
    qibuild.sh.mkdir(tmp_src, recursive=True)
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


def push_readme_v2(tmp, path, branch):
    """ Push version 2 of the readme to the git repo in the given branch

    """
    tmp_src = os.path.join(tmp, "src", path)
    tmp_srv = os.path.join(tmp, "srv", path)
    git = qisrc.git.Git(tmp_src)
    git.checkout("-f", branch)
    readme = os.path.join(tmp_src, "README")
    write_readme(tmp_src, "%s v2 on %s\n" % (path, branch))
    git.commit("-a", "-m", "README v2")
    git.push(tmp_srv, "%s:%s" % (branch, branch))



class GitTestCase(unittest.TestCase):
    def setUp(self):
        qibuild.command.CONFIG["quiet"] = True
        self.tmp = tempfile.mkdtemp(prefix="test-qisrc-sync")

    def tearDown(self):
        qibuild.command.CONFIG["quiet"] = True
        qibuild.sh.rm(self.tmp)

    def test_set_remote(self):
        bar_url = create_git_repo(self.tmp, "bar", with_release_branch=True)
        work = os.path.join(self.tmp, "work")
        qibuild.sh.mkdir(work)
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


class GitUpdateBranchTestCase(unittest.TestCase):
    def setUp(self):
        qibuild.command.CONFIG["quiet"] = True
        self.tmp = tempfile.mkdtemp(prefix="test-qisrc-sync")

    def tearDown(self):
        qibuild.command.CONFIG["quiet"] = True
        qibuild.sh.rm(self.tmp)

    def test_simple(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qibuild.sh.mkdir(work)
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
        qibuild.sh.mkdir(work)
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
        git.update_branch("master", "origin")
        git.checkout("master")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar v2 on master\n")

    def test_conflict(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qibuild.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Create conflicting changes
        write_readme(bar_src, "unstaged changes\n", append=True)
        push_readme_v2(self.tmp, "bar", "master")

        # Update branch: master should still have the unstaged changes
        err = git.update_branch("master", "origin")
        self.assertFalse(err is None)
        self.assertTrue("Merge conflict in README" in err)

        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar\nunstaged changes\n")

    def test_untracked_files(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qibuild.sh.mkdir(work)
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
        self.assertTrue(err is None)

        self.assertTrue(os.path.exists(a_file))
        with open(a_file, "r") as fp:
            contents = fp.read()
        self.assertEqual(contents, "a_file\n")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar v2 on master\n")

    def test_untracked_conflict(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qibuild.sh.mkdir(work)
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
        self.assertFalse(err is None)
        print err

    def test_wrong_branch_unstaged(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        qibuild.sh.mkdir(work)
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        # Checkout a 'next' branch with unstaged changes
        git.checkout("-b", "next")
        write_readme(bar_src, "bar on next\n")
        push_readme_v2(self.tmp, "bar", "master")

        err = git.update_branch("master", "origin")
        self.assertTrue(err is None)

        # Check we are still on next with our
        # unstaged changes back
        self.assertEqual(git.get_current_branch(), "next")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar on next\n")

        # Check that master is up to date
        git.checkout("-f", "master")
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar v2 on master\n")

    def test_set_tracking_banch_newly_created(self):
        bar_url = create_git_repo(self.tmp, "bar")
        work = os.path.join(self.tmp, "work")
        bar_src = os.path.join(work, "bar")
        git = qisrc.git.Git(bar_src)
        git.clone(bar_url)

        upstream_bar = os.path.join(self.tmp, "src", "bar")
        upstream_git = qisrc.git.Git(upstream_bar)
        upstream_git.checkout("-b", "release")
        upstream_git.push(bar_url, "release:release")

        git.set_tracking_branch("release", "origin")



if __name__ == "__main__":
    unittest.main()
