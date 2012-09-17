## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Build documentation."""

import qibuild
import qisrc.cmdparse
import qidoc.core

def configure_parser(parser):
    """Configure parser for this action."""
    qibuild.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser)

    parser.add_argument('project', nargs='?', help='Project to build.')

    group = parser.add_argument_group(title='build arguments')
    group.add_argument("--version", dest="version", action="store",
                       metavar="version", help="Documentation build version.")
    group.add_argument("--Werror", dest="werror", action="store_true",
                       help="treat warnings as errors", default=False)
    group.add_argument("--quiet-build", dest="quiet_build", action="store_true",
                       help="be quiet when building", default=False)
    group.add_argument("--release", dest="release", action="store_true",
                       default=False, help="build in release mode")
    group.add_argument("-D", dest="flags", action="append",
                       help="Add some sphinx compile flags")
    group.add_argument("-o", "--output-dir", dest="output_dir",
                       help="Where to generate the docs", default=None)
    group.add_argument("--full",  dest="full", action="store_true",
                       help="Force building of every project", default=False)

def do(args):
    """Main entry point."""
    projects = qisrc.cmdparse.projects_from_args(args)
    builder = qidoc.core.QiDocBuilder(projects, args.worktree, args.output_dir)
    opts = dict()
    opts['version'] = args.version if args.version else '0.42'
    opts['quiet'] = args.quiet_build
    opts["werror"] = args.werror
    opts["release"] = args.release
    flags = args.flags or list()
    if args.release:
        flags.insert(0, "build_type=release")
    opts["flags"] = flags
    builder.build(opts, project=(args.project if args.project else None))
