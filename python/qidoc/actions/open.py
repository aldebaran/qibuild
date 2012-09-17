## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Open the current documentation in a web browser."""

import qibuild
import qidoc.core

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)

    group = parser.add_argument_group(title='open actions')
    group.add_argument("-o", "--output-dir", dest="output_dir",
                       help="Where to generate the docs")
    group.add_argument("name", nargs="?", help="project to open")

def do(args):
    """ Main entry point """
    builder = qidoc.core.QiDocBuilder(args.worktree, args.output_dir)
    builder.open(project=args.name)
