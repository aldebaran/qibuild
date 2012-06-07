## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Install a project and its dependencies """

import os
import logging

import qibuild.install

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("install arguments")
    group.add_argument("--prefix", metavar="PREFIX",
        help="value of CMAKE_INSTALL_PREFIX, defaults to '/'")
    group.add_argument("destdir", metavar="DESTDIR")
    group.add_argument("--runtime", action="store_true",
        help="install runtime componenents only")
    group.add_argument("--include-deps", action="store_true", dest="include_deps",
        help="Include dependencies when installing (this is the default)")
    group.add_argument("--no-include-deps", action="store_false", dest="include_deps",
        help="Ignore dependencies when installing (use with caution)")
    parser.set_defaults(runtime=False, prefix="/", include_deps=True)

def do(args):
    """Main entry point"""
    toc      = qibuild.toc_open(args.worktree, args)
    qibuild.install.install_projects(toc, args.destdir, runtime=args.runtime,
                                     prefix=args.prefix,
                                     include_deps=args.include_deps)

