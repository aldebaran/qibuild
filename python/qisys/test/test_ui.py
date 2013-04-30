## Copyright (c) 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic tests for ui."""

import pytest

from qisys import ui

def test_indent_iterable():
    list_given = []
    list_given = ui.indent_iterable(list_given)
    list_expected = []
    assert list_given == list_expected

    list_given = ["a", "b", "c"]
    list_given = ui.indent_iterable(list_given)
    list_expected = ["  a", "  b", "  c"]
    assert list_given == list_expected

    list_given = ["a", "b", "c"]
    list_given = ui.indent_iterable(list_given, num=4)
    list_expected = ["    a", "    b", "    c"]
    assert list_given == list_expected

