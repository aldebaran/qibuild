## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Return the path to the activate file in the virtualenv

Mostly useful in scripts:

    source $(qibuild sourceme -q)
"""

import sys
import os

from qisys import ui

import qisys.error
import qisys.parsers
import qipy.parsers
import qibuild.parsers

def configure_parser(parser):
    qisys.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    if os.name == "nt":
        parser.add_argument("--mingw", action="store_true",
                          help="To be used from MinGW")
    parser.set_defaults(mingw=False)

def do(args):
    python_builder = qipy.parsers.get_python_builder(args)
    if args.mingw:
        win_extension=""
    else:
        win_extension=".bat"
    res = python_builder.python_worktree.bin_path("activate", win_extension=win_extension)
    if not os.path.exists(res):
        mess = """\
Could not find 'activate' script.
(%s does not exist)
Make sure to call `qipy bootstrap` first
""" % res
        raise qisys.error.Error(mess)

    if args.mingw:
        res = qisys.sh.to_posix_path(res, fix_drive=True)

    print res
    return res
