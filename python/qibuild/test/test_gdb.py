## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import subprocess

import qibuild.gdb


def run_gdb(base_dir):
    gdb_ini = os.path.join(base_dir, "gdb.ini")
    with open(gdb_ini, "w") as fp:
        fp.write("""file {binary}
run
bt
q
""".format(binary=os.path.join(base_dir, "bin/debugme")))
    cmd = ["gdb", "-batch", "-x", gdb_ini]
    process = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    return process.communicate()


def test_normal_debug(qibuild_action):
    proj = qibuild_action.add_test_project("debugme")
    qibuild_action("configure", "debugme")
    qibuild_action("make", "debugme")
    (out, _) = run_gdb(proj.sdk_directory)
    assert "in foo () at " in out
    assert "main.cpp" in out


def test_split_debug(qibuild_action):
    proj = qibuild_action.add_test_project("debugme")
    qibuild_action("configure", "debugme")
    qibuild_action("make", "debugme")
    qibuild.gdb.split_debug(proj.sdk_directory)
    (out, _) = run_gdb(proj.sdk_directory)
    assert "in foo () at " in out
    assert "main.cpp" in out


def test_split_debug_install(qibuild_action, tmpdir):
    tmpdir = tmpdir.strpath
    qibuild_action.add_test_project("debugme")
    qibuild_action("configure", "debugme")
    qibuild_action("make", "debugme")
    qibuild_action("install", "--runtime", "--split-debug", "debugme", tmpdir)
    (out, _) = run_gdb(tmpdir)
    assert "in foo () at " in out
    assert "main.cpp" in out
