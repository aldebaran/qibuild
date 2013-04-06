def test_simple(qitoolchain_action):
    qitoolchain_action("create", "foo")
    word_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo", "world", word_package)
