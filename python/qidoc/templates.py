## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""A set of tools to handle templates."""

import os

import qisys.sh

def configure_file(in_file, out_file,  opts=None, append_file=None):
    """Configure file from in_path to out_path,

    If opts is not None, use string.format() with the contents of
    the opts dictionnary.

    If append_file is not None, append the contents of the file to the output.

    If the file already exists and the contents of the file already are
    correct, do not write it.
    """
    if not os.path.exists(in_file):
        return
    with open(in_file, "r") as file_p:
        in_text = file_p.read()
    if opts:
        out_text = in_text.format(**opts)
    if append_file:
        with open(append_file, "r") as file_p:
            out_text += file_p.read()
    base_path = os.path.dirname(out_file)
    qisys.sh.mkdir(base_path, recursive=True)
    if os.path.exists(out_file):
        # Do not write if contents are correct:
        with open(out_file, "r") as file_p:
            contents = file_p.read()
        if contents == out_text:
            return
    with open(out_file, "w") as file_p:
        file_p.write(out_text)
