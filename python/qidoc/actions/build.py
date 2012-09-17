## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Build documentation."""

import qibuild
import qidoc.core

def configure_parser(parser):
    """Configure parser for this action."""
    qibuild.parsers.worktree_parser(parser)

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
    group.add_argument("--all",  dest="all", action="store_true",
                       help="Force building of every project", default=False)

def do(args):
    """Main entry point."""
    builder = qidoc.core.QiDocBuilder(args.worktree, args.output_dir)
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
    return
    # FIXME: Function stops here, dead code but replacing doesn't do exactly
    # what it used to do.
    # Build all if:
    #   user asked with --all,
    #   or a worktree has been given (so no point in using cwd())
    #   or we are at the root of the worktree.
#    if args.all or args.worktree or os.getcwd() == worktree:
#        builder.build(opts)
#        return
#    project_name = builder.project_from_cwd()
#    if not project_name:
#        # Not at the root, and could not guess current
#        # project: raise
#        mess  = "Could not guess project from current working directory\n"
#        mess += "Please go to the subdirectory of a project\n"
#        mess += "or specify a project name on the command line"
#        raise Exception(mess)
#    builder.build_single(project_name, opts)
