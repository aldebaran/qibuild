## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Common parsers for qisrc actions """

import qibuild.parsers

def worktree_parser(parser):
    qibuild.parsers.default_parser(parser)
    parser.add_argument("-w", "--worktree", "--work-tree", dest="worktree",
        help="Use a specific work tree path.")

