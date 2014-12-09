import os

import qisys.sh
import qitoolchain

def test_simple(qitoolchain_action, tmpdir, toolchains):
    this_dir = os.path.dirname(__file__)
    json_c_bz2_path_src = os.path.join(this_dir, "packages", "json-c-0.9.tbz2")
    json_c_bz2_path = tmpdir.join("json-c-0.9.tbz2").strpath
    qisys.sh.install(json_c_bz2_path_src, json_c_bz2_path)

    res = qitoolchain_action("convert-package",
                             "--name", "json-c",
                             "--batch", json_c_bz2_path)
    qitoolchain_action("create", "test")
    qitoolchain_action("add-package", "--config", "test", res)
    toolchain = qitoolchain.get_toolchain("test")
    assert toolchain.get_package("json-c")
