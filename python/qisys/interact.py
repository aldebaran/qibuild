# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

"""Small set of tools to interact with the user

"""

import os

import qisys
from qisys import ui


def read_input():
    """ Read input from the user

    """
    ui.info(ui.green, "> ", end="")
    return raw_input()


def ask_choice(choices, input_text, return_int=False):
    """Ask the user to choose from a list of choices

    """
    ui.info(ui.green, "::", ui.reset, input_text)
    for i, choice in enumerate(choices, start=1):
        if i == 1:
            choice += " \t(default)"
        ui.info("  ", ui.blue, "%i" % i, ui.reset, choice)
    keep_asking = True
    res = None
    while keep_asking:
        try:
            answer = read_input()
        except KeyboardInterrupt:
            break
        if not answer:
            return choices[0]
        try:
            index = int(answer)
        except ValueError:
            print "Please enter number"
            continue
        if index not in range(1, len(choices)+1):
            print "%i is out of range" % index
            continue
        res = choices[index-1]
        keep_asking = False

    if return_int:
        return index-1

    return res


def ask_yes_no(question, default=False):
    """Ask the user to answer by yes or no"""
    while True:
        if default:
            ui.info(ui.green, "::", ui.reset, question, "(Y/n)")
        else:
            ui.info(ui.green, "::", ui.reset, question, "(y/N)")
        answer = read_input()
        if answer.lower() in ["y", "yes"]:
            return True
        if answer.lower() in ["n", "no"]:
            return False
        if not answer:
            return default
        ui.warning("Please answer by 'yes' or 'no'")


def ask_string(question, default=None):
    """Ask the user to enter something.

    Returns what the user entered
    """
    if default:
        question += " (%s)" % default
    ui.info(ui.green, "::", ui.reset, question)
    try:
        answer = read_input()
    except KeyboardInterrupt:
        return default
    if not answer:
        return default
    return answer


def ask_program(message):
    """Ask the user to enter a path
    to a program.

    Look for it in PATH. If not found,
    ask the user to enter the full path.

    If still not found, give up ...
    """
    keep_going = True
    while keep_going:
        full_path = ask_string(message)
        if not full_path:
            break
        full_path = qisys.sh.to_native_path(full_path)
        if not os.path.exists(full_path):
            ui.error("%s does not exist" % full_path)
            keep_going = ask_yes_no("continue?")
            continue
        if not os.access(full_path, os.X_OK):
            ui.error("%s is not a valid executable!" % full_path)
            keep_going = ask_yes_no("continue?")
            continue
        return full_path


def ask_app(message):
    """ Ask the use to enter path to a .app """
    keep_going = True
    full_path = None
    while keep_going:
        full_path = ask_string(message)
        if not full_path:
            break
        full_path = qisys.sh.to_native_path(full_path)
        if not os.path.isdir(full_path):
            ui.error("%s does not exist or is not a directory" % full_path)
            keep_going = ask_yes_no("continue?")
        else:
            keep_going = False
    return full_path


def get_editor():
    """Find the editor searching the environment, lastly ask the user.

    Returns the editor.
    """
    editor = os.environ.get("VISUAL")
    if not editor:
        editor = os.environ.get("EDITOR")
    if not editor:
        # Ask the user to choose, and store the answer so
        # that we never ask again
        ui.warning("Could not find the editor to use.")
        editor = qisys.interact.ask_program("Please enter an editor")
    return editor
