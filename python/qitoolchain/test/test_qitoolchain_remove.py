## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qibuild.config
import qitoolchain.toolchain

from qibuild.test.conftest import TestBuildWorkTree

import pytest

def test_simple(qitoolchain_action):
    qitoolchain.toolchain.Toolchain("foo")
    qitoolchain_action("remove", "-f", "foo")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        qitoolchain.get_toolchain("foo")

def test_when_not_exists(qitoolchain_action):
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qitoolchain_action("remove", "foo")
    assert "No such toolchain" in str(e.value)

def test_when_is_default(qitoolchain_action):
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    test_build_worktre1 = TestBuildWorkTree()
    test_build_worktre1.set_default_config("foo")
    qitoolchain_action("remove", "foo", "--force")
    test_build_worktre2 = TestBuildWorkTree()
    # pylint:disable-msg=E1101
    with pytest.raises(Exception) as e:
        test_build_worktre2.toolchain
    assert "No such toolchain" in e.value.message
