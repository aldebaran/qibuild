## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import subprocess
from qibuild.test.test_toc import TestToc


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
