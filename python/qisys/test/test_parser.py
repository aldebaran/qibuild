import qisys.parser
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
    spam = worktree.create_project("spam")
    egss = worktree.create_project("spam/eggs")
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
