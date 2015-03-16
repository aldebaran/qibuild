## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate and return the path to a suitable 'sourceme' file

Useful when using a toolchain containing plugins

"""

from qisys import ui
import qibuild.parsers


def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)

def do(args):
    build_worktree = qibuild.parsers.get_build_worktree(args)
    sourceme = build_worktree.generate_sourceme()
    print sourceme
    return sourceme
