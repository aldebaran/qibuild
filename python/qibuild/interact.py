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
        answer = raw_input("> ")
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

def ask_yes_no(question):
    """Ask the user to answer by yes or no"""
    print "::", question, "(y/n)?"
    answer = raw_input("> ")
    return answer == "y"

def ask_string(question, default=None):
    """Ask the user to enter something.

    Returns what the user entered
    """
    if default:
        question += " (%s)" % default
    print "::", question
    answer = raw_input("> ")
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
    program = ask_string(message)
    full_path = qibuild.command.find_program(program)
    # TODO: hard-coded guess ?
    if full_path is not None:
        return full_path

    print "%s not found" % program
    full_path = ask_string("Please enter full path to %s" % program)
    full_path = qibuild.sh.to_native_path(full_path)
    if not os.path.exists(full_path):
        raise Exception("%s does not exists, aborting" % full_path)
    return full_path


