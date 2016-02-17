## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import sys
import os

import qisys.interact
from qisys.test.fake_interact import FakeInteract

import mock
import pytest

def test_ask_yes_no():
    """ Test that you can answer with several types of common answers """
    with mock.patch('__builtin__.raw_input') as m:
        m.side_effect = ["y", "yes", "Yes", "n", "no", "No"]
        expected_res  = [True, True, True, False, False, False]
        for res in expected_res:
            actual = qisys.interact.ask_yes_no("coffee?")
            assert actual == res

def test_ask_yes_no_default():
    """ Test that just pressing enter returns the default value """
    with mock.patch('__builtin__.raw_input') as m:
        m.side_effect = ["", ""]
        assert qisys.interact.ask_yes_no("coffee?", default=True)  is True
        assert qisys.interact.ask_yes_no("coffee?", default=False) is False

def test_ask_yes_no_wrong_input():
    """ Test that we keep asking when answer does not make sense """
    with mock.patch('__builtin__.raw_input') as m:
        m.side_effect = ["coffee!", "n"]
        assert qisys.interact.ask_yes_no("tea?") is False
        assert m.call_count == 2

def test_ask_string():
    with mock.patch('__builtin__.raw_input') as m:
        m.side_effect = ["sugar!", ""]
        res = qisys.interact.ask_string("coffee with what?")
        assert res == "sugar!"
        res = qisys.interact.ask_string("coffee with what?", default="milk")
        assert res == "milk"

def test_ask_program(record_messages):
    with mock.patch('__builtin__.raw_input') as m:
        # When not on Windows, we want to make sure the
        # result of ask_program is executable, that's why we
        # fake entering the current file (__file__) as input
        # On Windows, there's no way to tell, so we don't test this
        # case
        if os.name == "nt":
            m.side_effect = ["doesnotexists", "y",  sys.executable]
        else:
            m.side_effect = ["doesnotexists", "y",  __file__, "y", sys.executable]
        res = qisys.interact.ask_program("path to program")
        assert res == qisys.sh.to_native_path(sys.executable)
        assert record_messages.find("does not exist")
        if os.name != "nt":
            assert record_messages.find("is not a valid executable")

def test_get_editor_visual(monkeypatch):
    monkeypatch.setenv("VISUAL", "/usr/bin/vim")
    assert qisys.interact.get_editor() == "/usr/bin/vim"

def test_get_editor_editor(monkeypatch):
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.setenv("EDITOR", "/usr/bin/vim")
    assert qisys.interact.get_editor() == "/usr/bin/vim"

def test_get_editor_ask(monkeypatch):
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)
    with mock.patch('__builtin__.raw_input') as m:
        # Need something that won't change when we'll call
        # to_native_path() on the input
        if os.name == "nt":
            vim_path = r"c:\vim7\vim.exe"
        else:
            vim_path = "/usr/bin/vim"
        m.side_effect = [vim_path]
        with mock.patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            res = qisys.interact.get_editor()
            # On debian, /usr/bin/vim is often a symlink
            assert qisys.sh.samefile(res, vim_path)
            assert m.called

# pylint: disable-msg=E1101
@pytest.mark.skipif(sys.platform != "darwin",
                    reason="Onyl makes sense on Mac OSX")
def test_ask_app(tmpdir):
    foo_app_path = tmpdir.ensure("Applications/foo.app", dir=True)
    with mock.patch('__builtin__.raw_input') as m:
        m.side_effect = ["doesnotexists", "y", foo_app_path.strpath]
        assert qisys.interact.ask_app("foo") == foo_app_path.strpath
        assert len(m.mock_calls) == 3

def test_fake_interact_list():
    fake_interact = FakeInteract()
    fake_interact.answers = [False, "coffee!"]
    with mock.patch('qisys.interact', fake_interact):
        assert qisys.interact.ask_yes_no("tea?") is False
        assert qisys.interact.ask_string("then what?") == "coffee!"

def test_fake_interact_dict():
    fake_interact = FakeInteract()
    fake_interact.answers = {"coffee" : "y", "tea" : "n"}
    with mock.patch('qisys.interact', fake_interact):
        assert qisys.interact.ask_yes_no("Do you like tea?") == "n"
        assert qisys.interact.ask_yes_no("Do you like coffee?") == "y"

def test_questions_are_recorded():
    fake_interact = FakeInteract()
    fake_interact.answers = {"coffee" : "y", "tea" : "n"}
    with mock.patch('qisys.interact', fake_interact):
        assert qisys.interact.ask_yes_no("Do you like tea?") == "n"
        assert fake_interact.questions[0]['message'] == "Do you like tea?"
        assert fake_interact.questions[0]['default'] == False
