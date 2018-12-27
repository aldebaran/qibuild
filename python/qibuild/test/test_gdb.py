#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Gdb """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import subprocess

import qibuild.gdb
import qisys.command


def check_gdb():
    """ Check Gdb """
    gdb = qisys.command.find_program("gdb", raises=False)
    if not gdb:
        return False
    return True


def run_gdb(base_dir):
    """ Run Gdb """
    gdb_ini = os.path.join(base_dir, "gdb.ini")
    with open(gdb_ini, "w") as fp:
        fp.write(
            """file {binary}\nrun\nbt\nq\n""".format(
                binary=os.path.join(base_dir, "bin/debugme")
            )
        )
    cmd = ["gdb", "-batch", "-x", gdb_ini]
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.communicate()


def test_normal_debug(qibuild_action):
    """ Test Normal Debug """
    if not check_gdb():
        return
    proj = qibuild_action.add_test_project("debugme")
    qibuild_action("configure", "debugme")
    qibuild_action("make", "debugme")
    (out, _) = run_gdb(proj.sdk_directory)
    assert "in foo () at " in out
    assert "main.cpp" in out


def test_split_debug(qibuild_action):
    """ Test Split Debug """
    if not check_gdb():
        return
    proj = qibuild_action.add_test_project("debugme")
    qibuild_action("configure", "debugme")
    qibuild_action("make", "debugme")
    qibuild.gdb.split_debug(os.path.join(proj.sdk_directory, "bin", "debugme"))
    (out, _) = run_gdb(proj.sdk_directory)
    assert "in foo () at " in out
    assert "main.cpp" in out


def test_split_debug_install(qibuild_action, tmpdir):
    """ Test Split Debug Install """
    if not check_gdb():
        return
    tmpdir = tmpdir.strpath
    qibuild_action.add_test_project("debugme")
    qibuild_action("configure", "debugme")
    qibuild_action("make", "debugme")
    qibuild_action("install", "--runtime", "--split-debug", "debugme", tmpdir)
    (out, _) = run_gdb(tmpdir)
    assert "in foo () at " in out
    assert "main.cpp" in out


def test_gdb_not_installed(qibuild_action, tmpdir, record_messages):
    """ Test Gdb Not Installed """
    if check_gdb():
        return
    qibuild_action.add_test_project("debugme")
    qibuild_action("configure", "debugme")
    qibuild_action("make", "debugme")
    qibuild_action("install", "--runtime", "--split-debug",
                   "debugme", tmpdir.strpath)
    assert record_messages.find("Could not split debug symbols")
    assert tmpdir.check(dir=True)
