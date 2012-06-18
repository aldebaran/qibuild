## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Small set of tools to interact with the user

"""
#TODO: color!

import os

import qibuild


def ask_choice(choices, input_text):
    """Ask the user to choose from a list of choices

    """
    print "::", input_text
    for i, choice in enumerate(choices):
        print "  ", (i+1), choice
    keep_asking = True
    res = None
    while keep_asking:
        try:
            answer = raw_input("> ")
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
    if default:
        print "::", question, "(Y/n)?"
    else:
        print "::", question, "(y/N)?"
    try:
        answer = raw_input("> ")
    except KeyboardInterrupt:
        answer = "n"
    if not default:
        return answer == "y"
    else:
        return answer != "n"

def ask_string(question, default=None):
    """Ask the user to enter something.

    Returns what the user entered
    """
    if default:
        question += " (%s)" % default
    print "::", question
    try:
        answer = raw_input("> ")
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
            print "%s does not exists!" % full_path
            keep_going = ask_yes_no("continue")
            continue
        if not os.access(full_path, os.X_OK):
            print "%s is not a valid executable!" % full_path
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
        print "Could not find the editor to use."
        editor = qibuild.interact.ask_program("Please enter an editor")
    return editor
