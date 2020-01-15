#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Interact """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys
import six
import mock

import qisys.interact
from qisys.test.fake_interact import FakeInteract

if six.PY3:
    PATCHED_INPUT = "builtins.input"
else:
    PATCHED_INPUT = "__builtin__.raw_input"


def test_ask_yes_no():
    """ Test that you can answer with several types of common answers """
    with mock.patch(PATCHED_INPUT) as m:
        m.side_effect = ["y", "yes", "Yes", "n", "no", "No"]
        expected_res = [True, True, True, False, False, False]
        for res in expected_res:
            actual = qisys.interact.ask_yes_no("coffee?")
            assert actual == res


def test_ask_yes_no_default():
    """ Test that just pressing enter returns the default value """
    with mock.patch(PATCHED_INPUT) as m:
        m.side_effect = ["", ""]
        assert qisys.interact.ask_yes_no("coffee?", default=True) is True
        assert qisys.interact.ask_yes_no("coffee?", default=False) is False


def test_ask_yes_no_wrong_input():
    """ Test that we keep asking when answer does not make sense """
    with mock.patch(PATCHED_INPUT) as m:
        m.side_effect = ["coffee!", "n"]
        assert qisys.interact.ask_yes_no("tea?") is False
        assert m.call_count == 2


def test_ask_string():
    """ Test Ask String """
    with mock.patch(PATCHED_INPUT) as m:
        m.side_effect = ["sugar!", ""]
        res = qisys.interact.ask_string("coffee with what?")
        assert res == "sugar!"
        res = qisys.interact.ask_string("coffee with what?", default="milk")
        assert res == "milk"


def test_ask_program(record_messages):
    """ Test Ask Program """
    with mock.patch(PATCHED_INPUT) as m:
        m.side_effect = ["doesnotexists", "y", __file__, "y", sys.executable]
        res = qisys.interact.ask_program("path to program")
        assert res == qisys.sh.to_native_path(sys.executable)
        assert record_messages.find("does not exist")
        assert record_messages.find("is not a valid executable")


def test_get_editor_visual(monkeypatch):
    """ Test Get Editor Visual """
    monkeypatch.setenv("VISUAL", "/usr/bin/vim")
    assert qisys.interact.get_editor() == "/usr/bin/vim"


def test_get_editor_editor(monkeypatch):
    """ Test Get Editor Editor """
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.setenv("EDITOR", "/usr/bin/vim")
    assert qisys.interact.get_editor() == "/usr/bin/vim"


def test_get_editor_ask(monkeypatch):
    """ Test Get Editor Ask """
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)
    with mock.patch(PATCHED_INPUT) as m:
        m.side_effect = ["/usr/bin/vim"]
        res = qisys.interact.get_editor()
        assert res == qisys.sh.to_native_path("/usr/bin/vim")
        assert m.called


def test_ask_app(tmpdir):
    """ Test Ask App """
    foo_app_path = tmpdir.ensure("Applications/foo.app", dir=True)
    with mock.patch(PATCHED_INPUT) as m:
        m.side_effect = ["doesnotexists", "y", foo_app_path.strpath]
        assert qisys.interact.ask_app("foo") == foo_app_path.strpath
        assert len(m.mock_calls) == 3


def test_fake_interact_list():
    """ Test Fake Interact """
    fake_interact = FakeInteract()
    fake_interact.answers = [False, "coffee!"]
    with mock.patch('qisys.interact', fake_interact):
        assert qisys.interact.ask_yes_no("tea?") is False
        assert qisys.interact.ask_string("then what?") == "coffee!"


def test_fake_interact_dict():
    """ Test Fake Interact Dict """
    fake_interact = FakeInteract()
    fake_interact.answers = {"coffee": "y", "tea": "n"}
    with mock.patch('qisys.interact', fake_interact):
        assert qisys.interact.ask_yes_no("Do you like tea?") == "n"
        assert qisys.interact.ask_yes_no("Do you like coffee?") == "y"


def test_questions_are_recorded():
    """ Test Questions Are Recorded """
    fake_interact = FakeInteract()
    fake_interact.answers = {"coffee": "y", "tea": "n"}
    with mock.patch('qisys.interact', fake_interact):
        assert qisys.interact.ask_yes_no("Do you like tea?") == "n"
        assert fake_interact.questions[0]['message'] == "Do you like tea?"
        assert fake_interact.questions[0]['default'] is False
