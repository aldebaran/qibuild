#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import mock


def test_simple(qidoc_action):
    """ Test Simple """
    world_proj = qidoc_action.add_test_project("world")
    qidoc_action("build", "world")
    index_html = world_proj.index_html
    with mock.patch("webbrowser.open") as mock_open:
        qidoc_action("open", "world")
        index_html = mock_open.call_args[0][0]
        assert os.path.exists(index_html)


def test_open_translated(qidoc_action):
    """ Test open Translated """
    _translateme_proj = qidoc_action.add_test_project("translateme")
    qidoc_action("build", "translateme")
    with mock.patch("webbrowser.open") as mock_open:
        qidoc_action("open", "translateme")
        index_html = mock_open.call_args[0][0]
        assert os.path.exists(index_html)
    qidoc_action("build", "translateme", "--language", "fr")
    with mock.patch("webbrowser.open") as mock_open:
        qidoc_action("open", "translateme", "--language", "fr")
        index_html = mock_open.call_args[0][0]
        assert os.path.exists(index_html)
        with open(index_html, "r") as fp:
            assert "Cette page" in fp.read().decode("utf-8")
