## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Just some tests for ui """

import io

import qisys.error
import qisys.ui as ui


import pytest

def main():
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
    # pylint:disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        ui.valid_filename("foo/bar")
    # pylint:disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        ui.valid_filename("..")
    ui.valid_filename("foo")

def test_empty_end():
    out = io.BytesIO()
    ui.info("[skipped] ", end="", fp=out)
    ui.info("Your branch has diverged", fp=out)
    actual = out.getvalue()
    expected = "[skipped] Your branch has diverged\n"
    assert actual == expected

def test_several_newlines():
    out = io.BytesIO()
    ui.info("foo\n", "bar\n", "baz", fp=out)
    actual = out.getvalue()
    expected = "foo\nbar\nbaz\n"
    assert actual == expected

def test_do_not_add_space_after_newline():
    out = io.BytesIO()
    ui.info("foo\n", "bar", fp=out)
    actual = out.getvalue()
    expected = "foo\nbar\n"
    assert actual == expected

def test_insert_spaces():
    out = io.BytesIO()
    ui.info("foo:", "bar", fp=out)
    actual = out.getvalue()
    expected = "foo: bar\n"
    assert actual == expected

def test_custom_sep():
    out = io.BytesIO()
    ui.info("foo", "bar", sep="\n", fp=out)
    actual = out.getvalue()
    expected = "foo\nbar\n"
    assert actual == expected

def test_convert_to_strings():
    out = io.BytesIO()
    ui.info("mylist", ["a", "b", "c"], fp=out)
    actual = out.getvalue()
    expected = "mylist ['a', 'b', 'c']\n"
    assert actual == expected

def test_display_traceback(record_messages):
    def foo():
        bar()

    def bar():
        baz()

    def baz():
        raise Exception("Kaboom")

    try:
        foo()
    except Exception as e:
        message = ui.message_for_exception(e, "foo crashed")
    ui.error(*message)
    assert record_messages.find("foo crashed")
    # should contain the filename, a line number and the function name:
    assert record_messages.find(".*test_ui.py.*(\d+).*in.*bar")

if __name__ == "__main__":
    import sys
    if "-v" in  sys.argv:
        ui.CONFIG["verbose"] = True
    if "-q" in sys.argv:
        ui.CONFIG["quiet"]  = True
    main()
