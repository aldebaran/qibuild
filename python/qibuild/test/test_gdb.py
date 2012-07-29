## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import subprocess

import pytest

import qibuild
import qibuild.gdb
from qibuild.test.test_toc import TestToc


def run_gdb(base_dir):
    gdb_ini = os.path.join(base_dir, "gdb.ini")
    with open(gdb_ini, "w") as fp:
        fp.write("""file {binary}
run
bt
q
""".format(binary=os.path.join(base_dir, "bin/debugme")))
    cmd = ["gdb", "-batch", "-x",  gdb_ini]
    process = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    return process.communicate()


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_normal_debug():
    with TestToc() as toc:
        proj = toc.get_project("debugme")
        toc.configure_project(proj)
        toc.build_project(proj)
        (out, _)  = run_gdb(proj.sdk_directory)
        assert "in foo () at " in out
        assert "main.cpp" in out

# pylint: disable-msg=E1101
@pytest.mark.slow
def test_split_debug():
    with TestToc() as toc:
        proj = toc.get_project("debugme")
        toc.configure_project(proj)
        toc.build_project(proj)
        qibuild.gdb.split_debug(proj.sdk_directory)
        (out, _) = run_gdb(proj.sdk_directory)
        assert "in foo () at " in out
        assert "main.cpp" in out

# pylint: disable-msg=E1101
@pytest.mark.slow
def test_split_debug_install(tmpdir):
    with TestToc() as toc:
        tmpdir = tmpdir.strpath
        proj = toc.get_project("debugme")
        toc.configure_project(proj)
        toc.build_project(proj)
        toc.install_project(proj, tmpdir, split_debug=True, runtime=True)
        (out, _) = run_gdb(tmpdir)
        assert "in foo () at " in out
        assert "main.cpp" in out


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_gdb_release():
    with TestToc(build_type="Release") as toc:
        proj = toc.get_project("debugme")
        toc.configure_project(proj)
        toc.build_project(proj)
        (out, err) = run_gdb(proj.sdk_directory)
        assert "No stack" in err
        assert "in foo () at " not in out
