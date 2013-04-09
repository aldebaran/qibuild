import qisrc.git
import qisys.ui

import py

def setup_projects(qisrc_action):
    """ Create two git projects with one match for the
    "spam" pattern

    """
    foo_proj = qisrc_action.create_git_project("foo")
    bar_proj = qisrc_action.create_git_project("bar")

    # pylint: disable-msg=E1101
    foo_path = py.path.local(foo_proj.path)
    # pylint: disable-msg=E1101
    bar_path = py.path.local(bar_proj.path)

    foo_git = qisrc.git.Git(foo_proj.path)
    bar_git = qisrc.git.Git(bar_proj.path)

    foo_path.join("a.txt").write("this is spam\n")
    foo_git.add("a.txt")


def test_all_by_default(qisrc_action, record_messages):
    setup_projects(qisrc_action)
    record_messages.reset()
    rc = qisrc_action("grep", "spam", retcode=True)
    assert rc == 0
    assert qisys.ui.find_message("foo")
    assert qisys.ui.find_message("bar")
    assert qisys.ui.find_message("this is spam")

def test_using_projects(qisrc_action):
    setup_projects(qisrc_action)
    rc = qisrc_action("grep", "-p", "foo", "spam", retcode=True)
    assert rc == 0
    rc = qisrc_action("grep", "-p", "bar", "spam", retcode=True)
    assert rc == 1
