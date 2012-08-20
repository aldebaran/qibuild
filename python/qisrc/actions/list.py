## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the names and paths of every project, or those matching a pattern

"""

import re
import qibuild.log

LOGGER = qibuild.log.get_logger(__name__)

import qisrc
import qibuild


def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("pattern", metavar="PATTERN", nargs="?",
                        help="pattern to be matched")

def do(args):
    """ Main method """
    qiwt  = qisrc.open_worktree(args.worktree)
    regex = args.pattern
    if args.pattern is not None:
        regex = re.compile(regex)
    print "Projects in :", qiwt.root
    print
    for project in qiwt.projects:
        if regex is None or regex.search(project.src) is not None:
            print project.src
