def test_simple(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action("list")
    assert record_messages.find("world")

def test_empty(qibuild_action, record_messages):
    qibuild_action("list")
    assert record_messages.find("Please use")
