
from qisys import ui

def test_qisrc_foreach(qisrc_action, record_messages):
    qisrc_action("init")
    worktree = qisrc_action.worktree
    worktree.create_project("not_in_git")
    git_worktree = qisrc_action.git_worktree
    git_worktree.create_git_project("git_project")
    qisrc_action("foreach", "ls")
    assert not ui.find_message("not_in_git")
    assert ui.find_message("git_project")
    record_messages.reset()
    qisrc_action("foreach", "ls", "--all")
    assert ui.find_message("not_in_git")
    assert ui.find_message("git_project")
