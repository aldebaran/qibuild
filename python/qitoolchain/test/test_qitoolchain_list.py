## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_no_toolchain(qitoolchain_action, record_messages):
    qitoolchain_action("list")
    assert record_messages.find("No toolchain yet")

def test_list(qitoolchain_action, record_messages):
    qitoolchain_action("create", "foo")
    qitoolchain_action("list")
    assert record_messages.find("\* foo")
