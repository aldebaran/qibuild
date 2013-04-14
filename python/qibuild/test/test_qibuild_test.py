def test_various_outcomes(qibuild_action, record_messages):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qibuild_action("test", "testme", "-k", "ok")
    assert record_messages.find("All pass")
    record_messages.reset()

    rc = qibuild_action("test", "testme", "-k", "fail", retcode=True)
    assert record_messages.find("Return code: 1")
    assert rc == 1

    record_messages.reset()
    rc = qibuild_action("test", "testme", "-k", "segfault", retcode=True)
    assert record_messages.find("Segmentation fault")
    assert rc == 1

    record_messages.reset()
    rc = qibuild_action("test", "testme", "-k", "timeout", retcode=True)
    assert record_messages.find("Timed out")
    assert rc == 1
