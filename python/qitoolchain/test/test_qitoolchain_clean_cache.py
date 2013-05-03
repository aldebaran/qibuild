def test_simple(qitoolchain_action):
    qitoolchain_action("create", "foo")
    qitoolchain_action("clean-cache", "--force", "foo")
