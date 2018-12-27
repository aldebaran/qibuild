#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Config """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import mock

import qisys.script
import qibuild.config
from qibuild.test.conftest import TestBuildWorkTree


def test_show(qibuild_action):
    """ Just check it does not crash for now """
    qibuild_action("config")


def test_when_not_in_a_worktree(cd_to_tmpdir):
    """ Test When Not In A Worktree """
    qisys.script.run_action("qibuild.actions.config", list())


def test_edit(qibuild_action, interact):
    """ Test Edit """
    interact.editor = "/usr/bin/vim"
    global_xml = qibuild.config.get_global_cfg_path()
    with mock.patch("subprocess.call") as mock_call:
        qibuild_action("config", "--edit")
        assert mock_call.call_args_list == [
            mock.call(["/usr/bin/vim", global_xml])
        ]
        build_worktree = TestBuildWorkTree()
        local_xml = build_worktree.qibuild_xml
        mock_call.reset_mock()
        qibuild_action("config", "--edit", "--local")
        assert mock_call.call_args_list == [
            mock.call(["/usr/bin/vim", local_xml])
        ]


def test_run_wizard(qibuild_action, interact):
    """ Test Run Wizard """
    interact.answers = {
        "generator": "Unix Makefiles",
        "ide": "None",
    }
    qibuild_action("config", "--wizard")
