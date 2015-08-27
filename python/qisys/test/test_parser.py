## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.parsers
import qisys.worktree

import pytest

def test_guess_woktree(worktree, args):
    tmpdir = worktree.tmpdir
    bar = tmpdir.mkdir("foo").mkdir("bar")
    with qisys.sh.change_cwd(bar.strpath):
        assert qisys.parsers.get_worktree(args).root == worktree.root

def test_raises_when_not_in_worktree(tmpdir, args):
    with qisys.sh.change_cwd(tmpdir.strpath):
        # pylint: disable-msg=E1101
        with pytest.raises(qisys.worktree.NotInWorkTree):
            qisys.parsers.get_worktree(args)


def test_guess_current_project(worktree, args):
    libbar = worktree.create_project("lib/libbar")
    worktree.create_project("spam")
    worktree.create_project("spam/eggs")
    tmpdir = worktree.tmpdir

    # Simple check: when in the top dir of a project
    with qisys.sh.change_cwd(libbar.path):
        projects = qisys.parsers.get_projects(worktree, args)
        assert len(projects) == 1
        assert projects[0].src == "lib/libbar"

    # Should return the most nested project
    eggs_src = tmpdir.join("spam").join("eggs").mkdir("src")
    with qisys.sh.change_cwd(eggs_src.strpath):
        projects = qisys.parsers.get_projects(worktree, args)
        assert len(projects) == 1
        assert projects[0].src == "spam/eggs"

    # Should return None
    other = tmpdir.mkdir("other")
    with qisys.sh.change_cwd(other.strpath):
        assert not qisys.parsers.get_projects(worktree, args)

def test_parse_one_arg(worktree, args):
    foo = worktree.create_project("foo")

    # using '.' works
    with qisys.sh.change_cwd(foo.path):
        args.projects = ['.']
        projects = qisys.parsers.get_projects(worktree, args)
        assert len(projects) == 1
        assert projects[0].src == "foo"

    # using a project src with an explicit worktree works
    args.worktree = worktree.root
    args.projects = ["foo"]
    projects = qisys.parsers.get_projects(worktree, args)
    assert len(projects) == 1
    assert projects[0].src == "foo"

def test_auto_add_simple(worktree, args):
    tmpdir = worktree.tmpdir
    foo = tmpdir.mkdir("foo")
    qiproject_xml = foo.join("qiproject.xml")
    qiproject_xml.write("<project />")
    with qisys.sh.change_cwd(foo.strpath):
        args.projects = list()
        projects = qisys.parsers.get_projects(worktree, args)
        assert len(projects) == 1
        assert projects[0].src == "foo"

def test_auto_add_nested(worktree, args):
    tmpdir = worktree.tmpdir
    foo = worktree.create_project("foo")
    bar = worktree.create_project("foo/bar")
    baz = tmpdir.mkdir("foo", "bar", "baz")
    qiproject_xml = baz.join("qiproject.xml")
    qiproject_xml.write("<project />")
    assert len(worktree.projects) == 2
    with qisys.sh.change_cwd(baz.strpath):
        args.projects = list()
        projects = qisys.parsers.get_projects(worktree, args)
        assert len(projects) == 1
        assert projects[0].src == "foo/bar/baz"
    assert len(worktree.projects) == 3

    # But, now a clever guy adds <project src="baz" /> in
    # bar/qiproject.xml:
    bar_qiproject = tmpdir.join("foo", "bar", "qiproject.xml")
    bar_qiproject.write("""
<project>
  <project src="baz" />
</project>
""")
    worktree2 = qisys.worktree.WorkTree(tmpdir.strpath)
    assert len(worktree2.projects) == 3

def test_using_dash_all_with_dash_single(worktree, args):
    args.all = True
    args.single = True
    # pylint:disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.parsers.get_projects(worktree, args)
    assert "--single with --all" in e.value.message
