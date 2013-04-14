def test_simple(qibuild_action, record_messages):
    qibuild_action.add_test_project("nested")
    # only command we can be sure will always be there, even on
    # cmd.exe :)
    qibuild_action("foreach", "--", "python", "--version")
    assert record_messages.find("nested")
    assert record_messages.find("nested/foo")
