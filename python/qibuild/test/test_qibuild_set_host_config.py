# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import pytest

import qibuild.config


def test_set_host_config_happy_path(qibuild_action):
    qibuild.config.add_build_config("foo")
    qibuild_action("set-host-config", "foo")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    assert qibuild_cfg.get_host_config() == "foo"


def test_set_host_config_no_such_config(qibuild_action):
    # pylint:disable-msg=E1101
    with pytest.raises(Exception) as e:
        qibuild_action("set-host-config", "foo")
    assert "No such config" in e.value.message
