## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qisys.sh

from qisys.test.conftest import skip_on_win

@skip_on_win
def test_simple(qitoolchain_action, tmpdir, toolchains):
    toolchains.create("test")
    this_dir = os.path.dirname(__file__)
    json_c_bz2_path_src = os.path.join(this_dir, "packages", "json-c-0.9.tbz2")
    json_c_bz2_path = tmpdir.join("json-c-0.9.tbz2").strpath
    qisys.sh.install(json_c_bz2_path_src, json_c_bz2_path)
    qitoolchain_action("import-package", "--name", "json-c", "--batch",
                       json_c_bz2_path, "--toolchain", "test")
