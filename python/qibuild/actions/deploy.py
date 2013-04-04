## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Deploy project(s) on a remote target

All deployed material is installed in the location 'path' on
the target 'hostname'.

Examples:

  qibuild deploy foobar john@mytarget:deployed

Installs everything on the target 'mytarget' in the
'deployed' directory from the 'john' 's home.

  qibuild deploy foobar john@mytarget:/tmp/foobar

Installs everything on the target 'mytarget' in the
'/tmp/foobar' directory.
"""

import os

from qisys import ui
import qisys.sh
import qibuild.parsers
import qibuild.deploy

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("deploy options")
    group.add_argument("url", help="remote target url: user@hostname:path")
    group.add_argument("--port", help="port", type=int)
    group.add_argument("--split-debug", action="store_true",
                        dest="split_debug", help="split debug symbols. "
                        "Enable remote debuging")
    group.add_argument("--no-split-debug", action="store_false",
                        dest="split_debug", help="do not split debug symbols. "
                        "Remote debugging won't work")
    parser.set_defaults(port=22, split_debug=True)

def do(args):
    """Main entry point"""
    url = args.url
    qibuild.deploy.parse_url(url) # throws if url is invalid

    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    cmake_builder.deploy(url)

