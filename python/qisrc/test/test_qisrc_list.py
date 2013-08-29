def test_simple(qisrc_action, record_messages):
    qisrc_action.git_worktree.create_git_project("world")
    qisrc_action("list")
    assert record_messages.find("world")

def test_empty(qisrc_action, record_messages):
    qisrc_action("list")
    assert record_messages.find("Tips")
