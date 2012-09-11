## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Build documentation."""

import os

import qibuild
import qidoc.core

def configure_parser(parser):
    """Configure parser for this action."""
    qibuild.parsers.default_parser(parser)
    parser.add_argument("--work-tree", dest="worktree")
    parser.add_argument("--Werror", dest="werror",
        action="store_true",
        help="treat warnings as errors")
    parser.add_argument("--quiet-build", dest="quiet_build",
        action="store_true",
        help="be quiet when building")
    parser.add_argument("--version")
    parser.add_argument("name", nargs="?",
        help="project to build")
    parser.add_argument("--release", dest="release",
        action="store_true",
        help="build in release mode")
    parser.add_argument("-D", dest="flags",
        action="append",
        help="Add some sphinx compile flags")
    parser.add_argument("-o", "--output-dir", dest="output_dir",
        help="Where to generate the docs")
    parser.add_argument("--all",  dest="all", action="store_true",
        help="Force building of every project")
    parser.set_defaults(all=False, release=False)

def do(args):
    """Main entry point."""
    worktree = args.worktree
    worktree = qidoc.core.find_qidoc_root(worktree)
    if not worktree:
        raise Exception("No qidoc worktree found.\n"
          "Please call qidoc init or go to a qidoc worktree")
    output_dir = args.output_dir
    if not output_dir:
        output_dir = os.path.join(worktree, "build-doc")
    else:
        output_dir = qibuild.sh.to_native_path(output_dir)
    builder = qidoc.core.QiDocBuilder(worktree, output_dir)
    opts = dict()
    if args.version:
        opts["version"] = args.version
    else:
        opts["version"] = "0.42"
    if args.quiet_build:
        opts["quiet"] = True
    if args.werror:
        opts["werror"] = True
    opts["release"] = args.release
    flags = args.flags or list()
    if args.release:
        flags.insert(0, "build_type=release")
    opts["flags"] = flags
    if args.name:
        builder.build_single(args.name, opts)
        return
    # Build all if:
    #   user asked with --all,
    #   or a worktree has been given (so no point in using cwd())
    #   or we are at the root of the worktree.
    if args.all or args.worktree or os.getcwd() == worktree:
        builder.build_all(opts)
        return
    project_name = builder.project_from_cwd()
    if not project_name:
        # Not at the root, and could not guess current
        # project: raise
        mess  = "Could not guess project from current working directory\n"
        mess += "Please go to the subdirectory of a project\n"
        mess += "or specify a project name on the command line"
        raise Exception(mess)
    builder.build_single(project_name, opts)
