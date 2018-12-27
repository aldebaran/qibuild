#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Just some tests for ui """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import io
import sys
import pytest

import qisys.ui as ui


def main():
    """ Main Entry Point """
    ui.info(ui.red, "This is a an error message\n",
            ui.reset, "And here are the details")
    ui.error("could not build")
    ui.warning("-j ignored for this generator")
    ui.info("building foo")
    ui.debug("debug message")
    ui.info(ui.brown, "this is brown")
    ui.info(ui.bold, ui.brown, "this is bold brown")
    ui.info(ui.red, "red is dead")
    ui.info(ui.darkred, "darkred is really dead")
    ui.info(ui.yellow, "this is yellow")


def test_valid_filename():
    """ Test Valid FileName """
    with pytest.raises(Exception):
        ui.valid_filename("foo/bar")
    with pytest.raises(Exception):
        ui.valid_filename("..")
    ui.valid_filename("foo")


def test_empty_end():
    """ Test Empty End """
    out = io.BytesIO()
    ui.info("[skipped] ", end="", fp=out)
    ui.info("Your branch has diverged", fp=out)
    actual = out.getvalue().decode("utf-8")
    expected = "[skipped] Your branch has diverged\n"
    assert actual == expected


def test_several_newlines():
    """ Test Several New Lines """
    out = io.BytesIO()
    ui.info("foo\n", "bar\n", "baz", fp=out)
    actual = out.getvalue().decode("utf-8")
    expected = "foo\nbar\nbaz\n"
    assert actual == expected


def test_do_not_add_space_after_newline():
    """ Test Do Not Add Space After New Line """
    out = io.BytesIO()
    ui.info("foo\n", "bar", fp=out)
    actual = out.getvalue().decode("utf-8")
    expected = "foo\nbar\n"
    assert actual == expected


def test_insert_spaces():
    """ Test Insert Space """
    out = io.BytesIO()
    ui.info("foo:", "bar", fp=out)
    actual = out.getvalue().decode("utf-8")
    expected = "foo: bar\n"
    assert actual == expected


def test_custom_sep():
    """ Test Custom Sep """
    out = io.BytesIO()
    ui.info("foo", "bar", sep="\n", fp=out)
    actual = out.getvalue().decode("utf-8")
    expected = "foo\nbar\n"
    assert actual == expected


def test_convert_to_strings():
    """ Test Convert to Strings """
    out = io.BytesIO()
    ui.info("mylist", ["a", "b", "c"], fp=out)
    actual = out.getvalue().decode("utf-8")
    expected = "mylist ['a', 'b', 'c']\n"
    assert actual == expected


def test_convert_to_strings_unicode():
    """ Test Convert to Strings Unicode """
    out = io.BytesIO()
    ui.info("élément", ["Jérôme", "プログラミング"], fp=out)
    actual = out.getvalue().decode("utf-8")
    expected = "élément ['Jérôme', 'プログラミング']\n"
    assert actual == expected


def test_convert_to_strings_tuples():
    """ Test Convert to Strings Tuples """
    out = io.BytesIO()
    ui.info("mylist", ["a", ("b", "c"), "d"], fp=out)
    actual = out.getvalue().decode("utf-8")
    expected = "mylist ['a', ('b', 'c'), 'd']\n"
    assert actual == expected


if __name__ == "__main__":
    if "-v" in sys.argv:
        ui.CONFIG["verbose"] = True
    if "-q" in sys.argv:
        ui.CONFIG["quiet"] = True
    main()
