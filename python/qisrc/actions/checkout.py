## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Change the branch of the manifest

Also, checkout the correct branch for every git project
in the worktree

"""

from qisys import ui
import qisrc.parsers

import sys

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    group = parser.add_argument_group("checkout options")
    group.add_argument("branch")
    group.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Discard local changes. Use with caution")
    parser.set_defaults(force=False)

def do(args):
    branch = args.branch
    git_worktree = qisrc.parsers.get_git_worktree(args)
    manifest = git_worktree.manifest
    groups = manifest.groups
    branch = args.branch
    git_worktree.configure_manifest(manifest.url, groups=groups, branch=branch)
    ok = git_worktree.checkout(branch, force=args.force)
    if not ok:
        sys.exit(1)
