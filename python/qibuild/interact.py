## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Small set of tools to interact with the user

"""
#TODO: color!

import os

import qibuild
from qibuild import ui

def read_input():
    """ Read input from the user

    """
    ui.info(ui.green, "> ", end="")
    return raw_input()


def ask_choice(choices, input_text):
    """Ask the user to choose from a list of choices

    """
    ui.info(ui.green, "::", ui.reset, input_text)
    for i, choice in enumerate(choices):
        if i == 0:
            choice += " \t(default)"
        ui.info("  ", ui.blue, str(i+1), ui.reset, choice)
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

    return res

def ask_yes_no(question, default=False):
    """Ask the user to answer by yes or no"""
    while True:
        if default:
            ui.info(ui.green, "::", ui.reset, question, "(Y/n)?")
        else:
            ui.info(ui.green, "::", ui.reset, question, "(y/N)?")
        answer = read_input()
        if answer in ["y", "yes", "Yes"]:
            return True
        if answer in ["n", "no", "No"]:
            return False
        if not answer:
            return default
        ui.warning("Please anwser by 'yes' or 'no'")

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
        full_path = qibuild.sh.to_native_path(full_path)
        if not os.path.exists(full_path):
            ui.error("%s does not exists!" % full_path)
            keep_going = ask_yes_no("continue")
            continue
        if not os.access(full_path, os.X_OK):
            ui.error("%s is not a valid executable!" % full_path)
            keep_going = ask_yes_no("continue")
            continue
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
        editor = qibuild.interact.ask_program("Please enter an editor")
    return editor
