#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Fake Interact """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


class FakeInteract(object):
    """ A class to tests code depending on qisys.interact """

    def __init__(self):
        """ FakeInteract Init """
        self.answers_type = None
        self.answer_index = -1
        self._answers = None
        self.questions = list()
        self.editor = None

    @property
    def answers(self):
        """ Answers Getter """
        if self._answers is None:
            raise Exception("FakeInteract not initialized")
        return self._answers

    @answers.setter
    def answers(self, value):
        """ Answers Setter """
        if isinstance(value, dict):
            self.answers_type = "dict"
        elif isinstance(value, list):
            self.answers_type = "list"
        else:
            raise Exception("Unknow answer type: " + type(value))
        self._answers = value

    def find_answer(self, message, choices=None, default=None):
        """ Find Answer """
        keys = self.answers.keys()
        for key in keys:
            if key in message.lower():
                if not choices:
                    return self.answers[key]
                answer = self.answers[key]
                if answer in choices:
                    return answer
                else:
                    mess = "Would answer %s\n" % answer
                    mess += "But choices are: %s\n" % choices
                    raise Exception(mess)
        if default is not None:
            return default
        mess = "Could not find answer for\n  :: %s\n" % message
        mess += "Known keys are: %s" % ", ".join(keys)
        raise Exception(mess)

    def ask_choice(self, choices, message, **_unused):
        """ Ask Choice """
        print("::", message)
        for choice in choices:
            print("* ", choice)
        answer = self._get_answer(message, choices)
        print(">", answer)
        return answer

    def ask_yes_no(self, message, default=False):
        """ Ask Yes / No """
        print("::", message,)
        if default:
            print("(Y/n)")
        else:
            print("(y/N)")
        answer = self._get_answer(message, default=default)
        print(">", answer)
        return answer

    def ask_path(self, message):
        """ Ask Path """
        print("::", message)
        answer = self._get_answer(message)
        print(">", answer)
        return answer

    def ask_string(self, message):
        """ Ask String """
        print("::", message)
        answer = self._get_answer(message)
        print(">", answer)
        return answer

    def ask_program(self, message):
        """ Ask Program """
        print("::", message)
        answer = self._get_answer(message)
        print(">", answer)
        return answer

    def get_editor(self):
        """ Return the Editor """
        return self.editor

    def _get_answer(self, message, choices=None, default=None):
        """ Get an Answer """
        question = dict()
        question['message'] = message
        question['choices'] = choices
        question['default'] = default
        self.questions.append(question)
        if self.answers_type == "dict":
            return self.find_answer(message, choices=choices, default=default)
        self.answer_index += 1
        return self.answers[self.answer_index]
