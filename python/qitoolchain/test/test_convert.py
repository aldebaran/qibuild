## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

from qisys.test.conftest import skip_on_win
from qitoolchain.binary_package import convert_to_qibuild
import qitoolchain.qipackage

@skip_on_win
def test_convert_gentoo_package(tmpdir, toolchains):
    this_dir = os.path.dirname(__file__)
    json_c_bz2_path = os.path.join(this_dir, "packages", "json-c-0.9.tbz2")
    json_c_bz2 = qitoolchain.binary_package.open_package(json_c_bz2_path)
    converted = convert_to_qibuild(json_c_bz2,
            package_metadata={"name" : "json-c",
                              "version" : "0.9" },
            output_dir=tmpdir.strpath)
    tc_test = toolchains.create("test")
    package = qitoolchain.qipackage.from_archive(converted)
    assert package.name == "json-c"
    assert package.version == "0.9"
    package.path = tmpdir.strpath
    tc_test.add_package(package)
