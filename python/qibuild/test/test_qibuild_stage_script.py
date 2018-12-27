#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Stage Script """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import pytest

import qisys.command


def run_python_script(name):
    """ Run Python Script """
    args = [sys.executable, name]
    rcode = qisys.command.call(args)
    assert rcode == 0


def test_stage_script(qibuild_action, tmpdir):
    """ Test Stage Script """
    qibuild_action.add_test_project("world")
    project = qibuild_action.add_test_project("stagescript")
    qibuild_action("configure", "stagescript")
    qibuild_action("make", "stagescript")
    # Run from stage dir
    run_python_script(os.path.join(project.sdk_directory, 'bin', 'check_qipath'))
    # lib in this project
    run_python_script(os.path.join(project.sdk_directory, 'bin', 'dlopenfoo'))
    # lib with a dep in this project
    run_python_script(os.path.join(project.sdk_directory, 'bin', 'dlopenbar'))
    # lib with a dep in an other project
    run_python_script(os.path.join(project.sdk_directory, 'bin', 'dlopenworlduser'))
    # Now run them in install dir
    qibuild_action("install", "stagescript", tmpdir.strpath)
    # QI_PATH is only set by trampoline, so we expect next one to fail.
    with pytest.raises(Exception):
        run_python_script(os.path.join(tmpdir.strpath, 'bin', 'check_qipath'))
    run_python_script(os.path.join(tmpdir.strpath, 'bin', 'dlopenfoo'))
    run_python_script(os.path.join(tmpdir.strpath, 'bin', 'dlopenbar'))
    run_python_script(os.path.join(tmpdir.strpath, 'bin', 'dlopenworlduser'))
    # Now test an other project that uses those scripts
    qibuild_action.add_test_project("stagescript-user")
    qibuild_action("configure", "stagescript-user")
    qibuild_action("make", "stagescript-user")
    # Now cd somewhere and try again to run from the install dir.
    os.chdir('..')
    run_python_script(os.path.join(tmpdir.strpath, 'bin', 'dlopenfoo'))
    run_python_script(os.path.join(tmpdir.strpath, 'bin', 'dlopenbar'))
    run_python_script(os.path.join(tmpdir.strpath, 'bin', 'dlopenworlduser'))
