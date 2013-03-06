## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import pytest

import qisys
import qisrc
from qisrc.sync import clone_project
from qisrc.test.test_git import create_git_repo
from qisrc.test.test_git import create_git_repo_with_submodules

def create_worktree(tmpdir):
    work = tmpdir.mkdir("work")
    return qisys.worktree.WorkTree(work.strpath)

def test_simple(tmpdir):
    bar_url = create_git_repo(tmpdir.strpath, "bar")
    worktree = create_worktree(tmpdir)
    clone_project(worktree, bar_url)
    git_projects = qisrc.git.get_git_projects(worktree.projects)
    assert len(git_projects) == 1
    assert git_projects[0].src == "bar"

def test_project_already_exists(tmpdir):
    bar_url = create_git_repo(tmpdir.strpath, "bar")
    baz_url = create_git_repo(tmpdir.strpath, "baz")
    worktree = create_worktree(tmpdir)
    clone_project(worktree, bar_url, src="bar")
    # pylint: disable-msg=E1101
    with  pytest.raises(Exception) as e:
        qisrc.sync.clone_project(worktree, baz_url, src="bar")
    assert "already registered" in str(e.value)

def test_path_already_exists(tmpdir):
    bar_url = create_git_repo(tmpdir.strpath, "bar")
    worktree = create_worktree(tmpdir)
    tmpdir.join("work").mkdir("bar")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        clone_project(worktree, bar_url)
    assert "already exists" in str(e.value)
    clone_project(worktree, bar_url, src="baz")
    assert qisrc.git.get_git_projects(worktree.projects)[0].src == "baz"

def test_init_submodules(tmpdir):
    foo_url = create_git_repo_with_submodules(tmpdir.strpath)
    worktree = create_worktree(tmpdir)
    clone_project(worktree, foo_url)
    foo = worktree.get_project("foo")
    bar_readme = os.path.join(foo.path, "bar", "README")
    assert os.path.exists(bar_readme)
