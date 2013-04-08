import qisys.ui

def test_simple(qitoolchain_action, record_messages):
    foo_tc = qitoolchain_action("create", "foo")
    bar_tc = qitoolchain_action("create", "bar")
    world_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo", "world", world_package)
    record_messages.reset()
    qitoolchain_action("info")
    assert qisys.ui.find_message("foo")
    assert qisys.ui.find_message("world")
    assert qisys.ui.find_message("bar")
    record_messages.reset()
    qitoolchain_action("info", "foo")
    assert qisys.ui.find_message("foo")
    assert qisys.ui.find_message("world")
    assert not qisys.ui.find_message("bar")
