#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Toolchain Convert Package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest

import qisys.sh
import qitoolchain
import qibuild.config


def test_simple(qitoolchain_action, tmpdir, toolchains):
    """ Test Simple """
    this_dir = os.path.dirname(__file__)
    json_c_bz2_path_src = os.path.join(this_dir, "packages", "json-c-0.9.tbz2")
    json_c_bz2_path = tmpdir.join("json-c-0.9.tbz2").strpath
    qisys.sh.install(json_c_bz2_path_src, json_c_bz2_path)
    res = qitoolchain_action(
        "convert-package",
        "--name",
        "json-c",
        "--batch",
        json_c_bz2_path
    )
    qitoolchain_action("create", "test")
    qibuild.config.add_build_config("test", toolchain="test")
    qitoolchain_action("add-package", "--config", "test", res)
    toolchain = qitoolchain.get_toolchain("test")
    assert toolchain.get_package("json-c")


def test_rpm(qitoolchain_action, tmpdir):
    """ Test RPM """
    rpm = tmpdir.ensure("json-c-0.9.x86_64.rpm", file=True)
    with pytest.raises(NotImplementedError):
        qitoolchain_action(
            "convert-package",
            "--name",
            "json-c",
            "--batch",
            rpm.strpath
        )
