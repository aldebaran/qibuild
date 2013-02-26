## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisys.worktree

"""Parsing of commands arguments."""

def worktree_from_args(args):
    print "worktree_from_args is deprecated"
    print "use qisys.actions.get_worktree instead"
    import qisys.actions
    return qisys.actions.get_worktree(args)
