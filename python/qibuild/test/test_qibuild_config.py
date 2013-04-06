import qisys.command
import qibuild.cmake

import pytest

def test_simple(qibuild_action):
    # Just check it does not crash for now
    qibuild_action("config")

def test_run_wizard(qibuild_action):
    #qibuild_action("config", "--wizard")
