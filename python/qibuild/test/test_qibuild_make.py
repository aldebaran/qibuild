import os

import qisys.command

import pytest


def test_running_from_build_dir(qibuild_action):
    # Running `qibuild configure hello` `qibuild make hello` and running
    # the `hello` executable should work out of the box

    qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    hello = os.path.join(hello_proj.sdk_directory, "bin", "hello")
    qisys.command.call([hello])

def test_make_without_configure(qibuild_action):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    with pytest.raises(Exception) as e:
        qibuild_action("make", "-s", "hello")
    assert "The project world has not been configured yet" in str(e.value)
