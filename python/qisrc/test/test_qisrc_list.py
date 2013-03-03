from qisys import ui

def test_list_tips_when_empty(qisrc_action, record_messages):
    qisrc_action("init")
    qisrc_action("list")
    assert ui.find_message("Tips")
