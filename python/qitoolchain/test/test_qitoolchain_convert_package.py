## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qisys.sh
import qibuild.config
import qitoolchain

from qisys.test.conftest import skip_on_win

import pytest

@skip_on_win
def test_simple(qitoolchain_action, tmpdir, toolchains):
    this_dir = os.path.dirname(__file__)
    json_c_bz2_path_src = os.path.join(this_dir, "packages", "json-c-0.9.tbz2")
    json_c_bz2_path = tmpdir.join("json-c-0.9.tbz2").strpath
    qisys.sh.install(json_c_bz2_path_src, json_c_bz2_path)

    res = qitoolchain_action("convert-package",
                             "--name", "json-c",
                             "--batch", json_c_bz2_path)
    qitoolchain_action("create", "test")
    qibuild.config.add_build_config("test", toolchain="test")
    qitoolchain_action("add-package", "--config", "test", res)
    toolchain = qitoolchain.get_toolchain("test")
    assert toolchain.get_package("json-c")

@skip_on_win
def test_rpm(qitoolchain_action, tmpdir):
    rpm = tmpdir.ensure("json-c-0.9.x86_64.rpm", file=True)
    # pylint:disable-msg=E1101
    with pytest.raises(NotImplementedError):
        qitoolchain_action("convert-package", "--name", "json-c",
                           "--batch", rpm.strpath)
