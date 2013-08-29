def test_simple(qibuild_action, record_messages):
    # More complex tests should be written at a lower level
    qibuild_action.create_project("world")
    qibuild_action.create_project("hello", build_depends=["world"])
    qibuild_action("depends", "hello")
