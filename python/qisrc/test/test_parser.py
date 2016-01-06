## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.sh
import qisys.parsers
import qisrc.git
import qisrc.parsers
import qisrc.worktree

from qisrc.parsers import get_git_projects

from qibuild.test.conftest import TestBuildWorkTree
from qisrc.test.conftest import TestGitWorkTree

import mock
import pytest

def test_guess_git_repo(tmpdir, args):
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    foo = tmpdir.mkdir("foo")
    bar = foo.mkdir("bar")
    foo.join("qiproject.xml").write("""\
<project format="3">
  <project src="bar" />
</project>
""")
    worktree.add_project("foo")
    git = qisrc.git.Git(foo.strpath)
    git.init()
    git_worktree = qisrc.worktree.GitWorkTree(worktree)

    with qisys.sh.change_cwd(bar.strpath):
        assert qisys.parsers.get_projects(worktree, args)[0].src == "foo/bar"
        assert get_git_projects(git_worktree, args)[0].src == "foo"

def setup_test():
    build_worktree = TestBuildWorkTree()
    foo = build_worktree.create_project("foo")
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", build_depends=["world"])
    git = qisrc.git.Git(foo.path)
    git.init()
    git = qisrc.git.Git(world.path)
    git.init()
    git = qisrc.git.Git(hello.path)
    git.init()
    git_worktree = TestGitWorkTree()
    foo = git_worktree.get_git_project("foo")
    hello = git_worktree.get_git_project("hello")
    world = git_worktree.get_git_project("world")
    return (foo, hello, world)

def test_default_all(cd_to_tmpdir, args):
    (foo, hello, world) = setup_test()
    git_worktree = TestGitWorkTree()

    # Getting projects list at the top of the worktree is OK when using
    # default_all :
    projs = get_git_projects(git_worktree, args, default_all=True)
    assert projs == [foo, hello, world]

    # It's not when default_all is false
    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.worktree.NotInAGitRepo):
        get_git_projects(git_worktree, args, default_all=False)

def test_default_all_build_deps(cd_to_tmpdir, args):
    (foo, hello, world) = setup_test()
    git_worktree = TestGitWorkTree()

    # Getting projects list at the top of the worktree is OK when using
    # default_all and use_build_deps
    projs = get_git_projects(git_worktree, args,
                                           default_all=True,
                                           use_build_deps=True)
    assert projs == [foo, hello, world]

    # It's not when default_all is false
    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.worktree.NotInAGitRepo):
        get_git_projects(git_worktree, args,
                                       use_build_deps=True,
                                       default_all=False)

def test_build_deps(cd_to_tmpdir, args):
    args.dep_types = "default"
    (foo, hello, world) = setup_test()
    git_worktree = TestGitWorkTree()
    with qisys.sh.change_cwd(cd_to_tmpdir.join("hello").strpath):
        projs =  get_git_projects(git_worktree, args,
                                  use_build_deps=True,
                                  default_all=False)
        assert projs == [world, hello]
        projs = get_git_projects(git_worktree, args,
                                 use_build_deps=True,
                                 default_all=True)
        assert projs == [world, hello]

        args.single = True
        projs =  get_git_projects(git_worktree, args, use_build_deps=True)
        assert projs == [hello]

def test_build_deps_not_top_dir(cd_to_tmpdir, args):
    args.dep_types = "default"
    build_worktree = TestBuildWorkTree()
    dep_proj = build_worktree.create_project("dep")
    git = qisrc.git.Git(dep_proj.path)
    git.init()
    foo = build_worktree.create_project("foo", src="top/foo", build_depends=["dep"])
    top_proj = build_worktree.worktree.add_project("top")
    git = qisrc.git.Git(top_proj.path)
    git.init()
    git_worktree = TestGitWorkTree()
    top_proj = git_worktree.get_git_project("top")
    dep_proj = git_worktree.get_git_project("dep")
    with qisys.sh.change_cwd(cd_to_tmpdir.join("top", "foo").strpath):
        projs =  get_git_projects(git_worktree, args,
                                  use_build_deps=True)
        assert projs == [dep_proj, top_proj]


def test_groups(git_worktree, args):
    git_worktree = mock.Mock()
    args.groups = ["mygroup"]
    get_git_projects(git_worktree, args)
    assert git_worktree.get_git_projects.call_args_list == [mock.call(groups=["mygroup"])]


def test_no_duplicate_deps(cd_to_tmpdir, args):
    args.dep_types = "default"
    build_worktree = TestBuildWorkTree()
    foo = build_worktree.create_project("foo", run_depends=["bar"])
    build_worktree.create_project("bar", src="foo/bar")
    git = qisrc.git.Git(foo.path)
    git.init()
    git_worktree = TestGitWorkTree()

    with qisys.sh.change_cwd(cd_to_tmpdir.join("foo").strpath):
        projs = get_git_projects(git_worktree, args, default_all=True,
                                 use_build_deps=True)
    assert projs == [foo]
