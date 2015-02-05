## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_simple(qitoolchain_action):
    foo_tc = qitoolchain_action("create", "foo")
    assert foo_tc.packages == list()
