## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import argparse
import pytest

import qisrc.worktree
import qisrc.cmdparse

import qibuild.sh

def create_worktree(tmpdir):
    """ Helper function: Create a nice worktree with
    several git projects

    """
    worktree = qisrc.worktree.create(tmpdir.strpath)
    my_gui = tmpdir.mkdir("gui").mkdir("my_gui")
    worktree.add_project(my_gui.strpath)

    lib = tmpdir.mkdir("lib")
    lib_foo = lib.mkdir("libfoo")
    lib_foo.mkdir("src")
    worktree.add_project(lib_foo.strpath)

    lib_bar = lib.mkdir("libbar")
    lib_bar.mkdir("src")
    worktree.add_project(lib_bar.strpath)

    spam = tmpdir.mkdir("spam")
    worktree.add_project(spam.strpath)

    eggs = spam.mkdir("eggs")
    worktree.add_project(eggs.strpath)

    tmpdir.mkdir("other")

    return worktree

def parse_args(*args):
    """ Call qisrc.project_from_args, returns a list of projects sources


    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--worktree")
    parser.add_argument("projects", nargs="*")
    parser.add_argument("-a", "--all", action="store_true")
    parser.add_argument("-s", "--single", action="store_true")
    parsed_args = parser.parse_args(args=args)
    res = qisrc.cmdparse.projects_from_args(parsed_args)
    return [x.src for x in res]

def test_guess_current_project(tmpdir):
    worktree = create_worktree(tmpdir)

    # Simple check
    bar_src = tmpdir.join("lib").join("libbar").join("src")
    cur_proj = qisrc.cmdparse.guess_current_project(worktree, bar_src.strpath)
    assert cur_proj.src == worktree.get_project("lib/libbar").src

    # Should return the most nested project
    eggs_src = tmpdir.join("spam").join("eggs").join("src")
    cur_proj = qisrc.cmdparse.guess_current_project(worktree, eggs_src.strpath)
    assert cur_proj.src == worktree.get_project("spam/eggs").src

    # Should return None
    other = tmpdir.join("other")
    assert qisrc.cmdparse.guess_current_project(worktree, other.strpath) is None

def test_worktree_given(tmpdir):
    worktree = create_worktree(tmpdir)

    # No arg -> return all
    res = parse_args("--worktree", worktree.root)
    assert res == ["gui/my_gui", "lib/libbar", "lib/libfoo", "spam", "spam/eggs"]

def test_using_all(tmpdir):
    worktree = create_worktree(tmpdir)
    libbar = tmpdir.join("lib").join("libbar").join("src")
    with qibuild.sh.change_cwd(libbar.strpath):
        res = parse_args("--all")
        assert res == ["gui/my_gui", "lib/libbar", "lib/libfoo", "spam", "spam/eggs"]

def test_no_arg(tmpdir):
    worktree = create_worktree(tmpdir)

    # subdir of a project:
    libbar = tmpdir.join("lib").join("libbar").join("src")
    with qibuild.sh.change_cwd(libbar.strpath):
        res = parse_args()
        assert res == ["lib/libbar"]

    # directory containing several projects
    lib = tmpdir.join("lib")
    with qibuild.sh.change_cwd(lib.strpath):
        res = parse_args()
        assert res == ["lib/libbar", "lib/libfoo"]

    # root of the worktree:
    with qibuild.sh.change_cwd(worktree.root):
        res = parse_args()
        assert res == ["gui/my_gui", "lib/libbar", "lib/libfoo", "spam", "spam/eggs"]

    # other
    other = tmpdir.join("other")
    with qibuild.sh.change_cwd(other.strpath):
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            parse_args()
        assert "Could not find any project in " in str(e)

def test_one_arg(tmpdir):
    worktree = create_worktree(tmpdir)

    # As a path (1)
    with qibuild.sh.change_cwd(worktree.root):
        res = parse_args("lib")
        assert res == ["lib/libbar", "lib/libfoo"]

    # As a path (2)
    gui = tmpdir.join("gui")
    with qibuild.sh.change_cwd(gui.strpath):
        res = parse_args("../lib")
        assert res == ["lib/libbar", "lib/libfoo"]

    # As a project name:
    gui = tmpdir.join("gui")
    with qibuild.sh.change_cwd(gui.strpath):
        res = parse_args("lib/libbar")
        assert res == ["lib/libbar"]

    # Non existing project name:
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        parse_args("--worktree", worktree.root, "does/no/exist")
    assert "No project in" in str(e)

    # Subdir of a project should also raise when it's explicit
    # (ie, not guessed from cwd):
    with qibuild.sh.change_cwd(worktree.root):
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            parse_args("lib/libbar/src")
        assert "Could not find any project" in str(e)


def test_single(tmpdir):
    worktree = create_worktree(tmpdir)
    spam = tmpdir.join("spam")
    with qibuild.sh.change_cwd(spam.strpath):
        assert parse_args("-s") == ["spam"]
        assert parse_args() == ["spam", "spam/eggs"]

    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        parse_args("-s", "lib/libfoo", "spam/eggs")

    assert "Using --single with several projects does not make sense" in str(e)

    with qibuild.sh.change_cwd(worktree.root):
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            parse_args("-s", "lib")
        assert "No project in 'lib'" in str(e)

        assert parse_args("spam/eggs", "-s") == ["spam/eggs"]
