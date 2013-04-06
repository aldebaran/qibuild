import qisys.ui

def test_various_outcomes(qibuild_action, record_messages):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qibuild_action("test", "testme", "-k", "ok")
    assert qisys.ui.find_message("All pass")
    record_messages.reset()

    rc = qibuild_action("test", "testme", "-k", "fail", retcode=True)
    assert qisys.ui.find_message("Return code: 1")
    assert rc == 1

    record_messages.reset()
    rc = qibuild_action("test", "testme", "-k", "segfault", retcode=True)
    assert qisys.ui.find_message("Segmentation fault")
    assert rc == 1

    record_messages.reset()
    rc = qibuild_action("test", "testme", "-k", "timeout", retcode=True)
    assert qisys.ui.find_message("Timed out")
    assert rc == 1
