## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
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


import qibuild.parsers
import qibuild.deploy

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("deploy options")
    group.add_argument("url", help="remote target url: user@hostname:path")
    group.add_argument("--port", help="port", type=int, default=22)
    group.add_argument("--split-debug", action="store_true", dest="split_debug",
                        help="split debug symbols. Enable remote debuging")
    group.add_argument("--url", dest="urls", action="append", help="deploy to each given url.")
    group.add_argument("--no-tests", action="store_const",
                       const=["runtime"], dest="dep_types",
                       help="Work on specified projects by ignoring "
                            "the test deps")
    parser.set_defaults(dep_types="default")

def do(args):
    """Main entry point"""
    if args.urls:
        urls = args.urls + [args.url]
    else:
        urls = [args.url]

    for url in urls:
        # make sure every url is valid first
        parsed = qibuild.deploy.parse_url(url)
        if not parsed:
            mess = """ Could not parse {0} as a valid deploy url.
Supported formats are:
   * <user>@<host>:<deploy-dir>
   * ssh://<user>@<host>:<port>/<deploy-dir>
"""
            raise Exception(mess.format(url))

    cmake_builder = qibuild.parsers.get_cmake_builder(
                                    args, default_dep_types=["test", "runtime"])

    cmake_builder.build()
    for url in urls:
        cmake_builder.deploy(url, split_debug=args.split_debug)
