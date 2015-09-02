## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Make all python projects available in the current build configuration

"""
import sys
import os

from qisys import ui
import qisys.sh
import qisys.command
import qisys.parsers
import qibuild.parsers
import qipy.parsers
import qipy.worktree

def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("requirements", nargs="*")
    parser.add_argument("--no-site-packages", action="store_false",
                        dest="site_packages",
                        help="Do not allow access to global `site-packages` "
                             "directory")
    parser.add_argument("-p", "--python",
                        help="The Python interpreter to use")
    parser.set_defaults(requirements=["pip", "virtualenv", "ipython"],
                        site_packages=True)

def do(args):
    python_builder = qipy.parsers.get_python_builder(args)
    ok = python_builder.bootstrap(remote_packages=args.requirements,
                                  site_packages=args.site_packages,
                                  python_executable=args.python)
    if not ok:
        sys.exit(1)
