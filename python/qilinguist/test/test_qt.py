## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from __future__ import print_function

import os
import subprocess

import pytest

import qisys.command
import qisys.error
import qisys.qixml
import qibuild.find

from qibuild.test.conftest import TestBuildWorkTree
from qilinguist.test.conftest import skip_no_lrelease

@skip_no_lrelease
def test_qt(qilinguist_action):
    build_worktree = TestBuildWorkTree()
    project = build_worktree.add_test_project("translateme/qt")
    try:
        project.configure()
    except qisys.error.Error:
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
