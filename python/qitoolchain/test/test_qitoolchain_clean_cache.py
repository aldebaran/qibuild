def test_simple(qitoolchain_action):
    foo_tc = qitoolchain_action("create", "foo")
    qitoolchain_action("clean-cache", "--force", "foo")
