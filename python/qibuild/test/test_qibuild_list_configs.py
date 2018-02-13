
# pylint: disable=unused-variable


def test_list(qibuild_action, toolchains, record_messages):
    toolchains.create("foo")
    qibuild_action("add-config", "foo", "--toolchain", "foo")
    qibuild_action("add-config", "bar", "--profile", "bar")
    record_messages.reset()
    qibuild_action("list-configs")
    from qisys import ui
    assert record_messages.find("foo\n  toolchain: foo")
    assert record_messages.find("bar\n  profiles: bar")
