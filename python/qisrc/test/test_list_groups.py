def test_list_groups(qisrc_action, git_server, record_messages):
    git_server.create_group("default", ["foo", "bar"], default=True)
    git_server.create_group("spam", ["spam", "eggs"])
    qisrc_action("init", git_server.manifest_url)
    record_messages.reset()
    qisrc_action("list-groups")
    assert record_messages.find("\* default")
    assert record_messages.find(" spam")
