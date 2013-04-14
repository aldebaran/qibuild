def test_no_cmake(qibuild_action, record_messages):
    qibuild_action.add_test_project("convert/no_cmake")
    qibuild_action.chdir("convert/no_cmake")
    qibuild_action("convert")
    assert record_messages.find("Would create")
    assert record_messages.find("--go")
    record_messages.reset()
    qibuild_action("convert", "--go")
    qibuild_action("configure")
    qibuild_action("make")

def test_pure_cmake(qibuild_action):
    qibuild_action.add_test_project("convert/pure_cmake")
    qibuild_action("convert", "--go")
    qibuild_action.chdir("convert/pure_cmake")
    qibuild_action("configure")

def test_convert_1_14(qibuild_action):
    pass
