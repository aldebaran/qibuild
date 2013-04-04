## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Install a project and its dependencies """

import os

import qisys.sh
import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("install options")
    group.add_argument("--prefix", metavar="PREFIX",
        help="value of CMAKE_INSTALL_PREFIX, defaults to '/'")
    group.add_argument("dest_dir", metavar="DESTDIR")
    group.add_argument("--include-deps", action="store_true", dest="include_deps",
        help="Include dependencies when installing (this is the default)")
    group.add_argument("--no-include-deps", action="store_false", dest="include_deps",
        help="Ignore dependencies when installing (use with caution)")
    group.add_argument("--split-debug", action="store_true", dest="split_debug",
        help="Split the debug symbols out of the binaries")
    parser.set_defaults(runtime=False, prefix="/", include_deps=True)
    if not parser.epilog:
        parser.epilog = ""
    parser.epilog += """
Warning:
    If CMAKE_INSTALL_PREFIX was set during configure, it is necessary to repeat
    it at install using the '--prefix' option.
"""


def do(args):
    """Main entry point"""
    # Compute final destination:
    dest_dir = qisys.sh.to_native_path(args.dest_dir)

    cmake_builder = qibuild.parsers.get_cmake_builder(args)

    cmake_builder.install(dest_dir)
