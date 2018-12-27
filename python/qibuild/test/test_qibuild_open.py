#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Open """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import mock

import qibuild.config


def test_no_ide_yet(qibuild_action, record_messages):
    """ Test No Ide Yet """
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")
    qibuild_action("open", "world")
    assert record_messages.find("No IDE configured yet")


def test_run_configure(qibuild_action, interact):
    """ Test Run Configure """
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    qtcreator = qibuild.config.IDE()
    qtcreator.name = "QtCreator"
    qtcreator.path = "/usr/local/bin/qtcreator"
    qibuild_cfg.add_ide(qtcreator)
    qibuild_cfg.write()
    world_proj = qibuild_action.add_test_project("world")
    interact.answers = [True]
    with mock.patch("qibuild.actions.open.open_qtcreator") as open_qtcreator:
        qibuild_action("open", "world")
        assert open_qtcreator.called_with(world_proj, "/usr/local/bin/qtcreator")
