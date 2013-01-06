## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisys.worktree

"""Parsing of commands arguments."""

def worktree_from_args(args):
    if args.worktree:
        worktree_was_explicit = True
        root = args.worktree
    else:
        worktree_was_explicit = False
        root = qisys.worktree.guess_worktree(raises=True)

    worktree = qisys.worktree.open_worktree(args.worktree)

    return (worktree_was_explicit, worktree)
