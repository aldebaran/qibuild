## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import tempfile
import unittest

import qisrc.git
import qibuild.sh

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
    readme = os.path.join(tmp_src, "README")
    with open(readme, "w") as fp:
        fp.write(path + "\n")
    git = qisrc.git.Git(tmp_src)
    git.call("init")
    git.call("add", ".")
    git.call("commit", "-m", "intial commit")
    git.call("push", tmp_srv, "master:master")

    if not with_release_branch:
        return tmp_srv

    git.checkout("-b", "release-1.12")
    with open(readme, "w") as fp:
        fp.write(path + " on release-1.12\n")
    git.call("add", "README")
    git.call("commit", "-m", "update README for 1.12")
    git.call("push", tmp_srv, "release-1.12:release-1.12")
    return tmp_srv

def read_readme(src):
    """ Returns the contents for the README file
    Useful to check on what branch we are

    """
    readme = os.path.join(src, "README")
    with open(readme, "r") as fp:
        return fp.read()

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
        git.safe_checkout("master", tracks="origin")
        git.pull()
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar\n")
        git.safe_checkout("stable", tracks="origin", remote_branch="release-1.12")
        git.pull()
        readme = read_readme(bar_src)
        self.assertEqual(readme, "bar on release-1.12\n")



if __name__ == "__main__":
    unittest.main()
