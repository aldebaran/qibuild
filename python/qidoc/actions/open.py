## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Open the current documentation in a web browser."""

import qibuild
import qidoc.core
import qisrc.cmdparse

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser)

    group = parser.add_argument_group(title='open actions')
    group.add_argument("-o", "--output-dir", dest="output_dir",
                       help="Where to generate the docs")
    group.add_argument("name", nargs="?", help="project to open")

def do(args):
    """ Main entry point """
    projects = qisrc.cmdparse.projects_from_args(args)
    builder = qidoc.core.QiDocBuilder(projects, args.worktree, args.output_dir)
    builder.open(project=args.name)
