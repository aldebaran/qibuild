## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import pytest
import os

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qibuild.actions import run

def test_run_target(qibuild_action):
    project = qibuild_action.add_test_project("testme")
    project.configure()
    project.build()

    retcode = qibuild_action("run", "ok", retcode=True)
    assert retcode == 0

def test_run_failing_binary(qibuild_action):
    project = qibuild_action.add_test_project("testme")
    project.configure()
    project.build()

    retcode = qibuild_action("run", "fail", retcode=True)
    assert retcode == 1

def test_run_segfaulting_binary(qibuild_action, record_messages):
    project = qibuild_action.add_test_project("testme")
    project.configure()
    project.build()

    retcode = qibuild_action("run", "segfault", retcode=True)
    if os.name != 'nt':
        # on Windows the python process may be interrupted by
        # the OS with a pop up 'segfault_d.exe has stopped working'
        # so we may not get the error message
        assert record_messages.find("Process crashed")
    assert retcode != 0

def test_run_failure(qibuild_action):
    project = qibuild_action.add_test_project("testme")
    project.configure()
    project.build()

    e = qibuild_action("run", "idontexist", raises=True)
    assert e == "idontexist not found"
