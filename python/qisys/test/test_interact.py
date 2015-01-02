## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisys.interact
from qisys.test.fake_interact import FakeInteract

import mock



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
