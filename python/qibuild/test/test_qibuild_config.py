## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest

import qibuild.config

def test_show(qibuild_action):
    # Just check it does not crash for now
    qibuild_action("config")

def test_run_wizard(qibuild_action, interact):
    interact.answers = {
        "generator" : "Unix Makefiles",
        "ide" : "None",
    }

    qibuild_action("config", "--wizard")
