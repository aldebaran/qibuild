import qisys.ui

def test_simple(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action("list")
    assert qisys.ui.find_message("world")

def test_empty(qibuild_action, record_messages):
    qibuild_action("list")
    assert qisys.ui.find_message("Please use")
