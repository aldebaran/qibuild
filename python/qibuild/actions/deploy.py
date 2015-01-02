## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
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


import qisys.parsers
import qibuild.parsers
import qisys.parsers
import qibuild.deploy

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    qisys.parsers.deploy_parser(parser)
    group = parser.add_argument_group("qibuild specific deploy options")
    group.add_argument("--split-debug", action="store_true", dest="split_debug",
                       help="split debug symbols. Enable remote debuging")
    group.add_argument("--with-tests", dest="with_tests", action="store_true",
                       help="also deploy the tests")
    parser.set_defaults(with_tests=False)

def do(args):
    """Main entry point"""

    urls = qisys.parsers.get_deploy_urls(args)

    if args.with_tests:
        default_dep_types = ["runtime", "test"]
    else:
        default_dep_types = ["runtime"]
    cmake_builder = qibuild.parsers.get_cmake_builder(
                                    args, default_dep_types=default_dep_types)
    for url in urls:
        cmake_builder.deploy(url, split_debug=args.split_debug,
                             with_tests=args.with_tests)
