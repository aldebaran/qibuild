# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import os

import mock

# pylint: disable=unused-variable


def test_simple(qidoc_action):
    world_proj = qidoc_action.add_test_project("world")
    qidoc_action("build", "world")
    index_html = world_proj.index_html
    with mock.patch("webbrowser.open") as mock_open:
        qidoc_action("open", "world")
        index_html = mock_open.call_args[0][0]
        assert os.path.exists(index_html)


def test_open_translated(qidoc_action):
    translateme_proj = qidoc_action.add_test_project("translateme")
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
            assert "Cette page" in fp.read()
