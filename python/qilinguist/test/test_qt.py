#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import subprocess

import qisys.qixml
import qibuild.find
from qibuild.test.conftest import TestBuildWorkTree


def test_qt(qilinguist_action):
    """ Test Qt """
    build_worktree = TestBuildWorkTree()
    project = build_worktree.add_test_project("translateme/qt")
    try:
        project.configure()
    except Exception:
        print("Qt not installed, skipping")
        return
    project.build()
    qilinguist_action("update", "helloqt")
    # Translate in French:
    fr_ts = os.path.join(project.path, "po", "fr_FR.ts")
    tree = qisys.qixml.read(fr_ts)
    root = tree.getroot()
    tr_elem = root.find("context/message/translation")
    assert tr_elem is not None
    tr_elem.attrib.clear()
    tr_elem.text = "Bonjour, monde"
    qisys.qixml.write(root, fr_ts)
    qilinguist_action("release", "helloqt")
    translateme = qibuild.find.find([project.sdk_directory], "translateme")
    cmd = [translateme,
           os.path.join(project.path, "po"),
           "fr_FR"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    (out, _) = process.communicate()
    assert "Bonjour, monde" in out
