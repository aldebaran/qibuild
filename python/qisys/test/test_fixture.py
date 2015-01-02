## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import qisys.sh
from qisys import ui

from qisys.test.conftest import skip_on_win

def test_worktree(worktree):
    assert len(worktree.projects) == 0
    assert os.path.exists(worktree.worktree_xml)

def test_tmp_conf():
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    assert os.path.exists(os.path.dirname(qibuild_xml))
    assert not os.path.exists(qibuild_xml)

def test_record(record_messages):
    ui.info("foo is 42")
    assert record_messages.find("foo")
    assert not record_messages.find("bar")
    record_messages.reset()
    assert not record_messages.find("foo")

def test_cd_to_tmp(cd_to_tmpdir):
    assert os.listdir(os.getcwd()) == list()

@skip_on_win
def test_skip_on_win():
    assert os.name != 'nt'
