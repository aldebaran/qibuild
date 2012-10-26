## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import subprocess
from qibuild.test.test_toc import TestToc

import pytest

def test_config_h(tmpdir):
    with TestToc() as toc:
        proj = toc.get_project("config_h")
        toc.configure_project(proj)
        toc.build_project(proj)
        toc.install_project(proj, tmpdir.strpath)
        foo = os.path.join(proj.sdk_directory, "bin", "foo")
        process = subprocess.Popen([foo])
        process.wait()
        assert process.returncode == 42
        assert tmpdir.join("include", "foo", "config.h").check(file=1)

#pylint: disable-msg=E1101
@pytest.mark.xfail
def test_config_h_extra_install_rule(tmpdir):
    with TestToc(cmake_flags=["WITH_EXTRA_INSTALL_RULE=ON"]) as toc:
        proj = toc.get_project("config_h")
        toc.configure_project(proj, )
        toc.build_project(proj)
        toc.install_project(proj, tmpdir.strpath)
        full_config_h = os.path.join(proj.build_directory, "include", "foo", "config.h")
        full_config_h = os.path.join(tmpdir.strpath, full_config_h)
        assert not os.path.exists(full_config_h)
