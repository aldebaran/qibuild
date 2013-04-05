import qisys.command
import qibuild.cmake

import pytest

def test_simple(qibuild_action):
    # Just check it does not crash for now
    qibuild_action("config")
