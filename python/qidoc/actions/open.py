## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Open the current documentation in a web browser."""

import os

import qibuild
import qidoc.core

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.default_parser(parser)
    parser.add_argument("--work-tree", dest="worktree")
    parser.add_argument("-o", "--output-dir", dest="output_dir",
        help="Where to generate the docs")
    parser.add_argument("name", nargs="?",
        help="project to open")

def do(args):
    """ Main entry point """
    worktree = args.worktree
    project_name = args.name

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
    if project_name:
        builder.open_single(project_name)
        return
    project_name = builder.project_from_cwd()
    if project_name:
        builder.open_single(project_name)
        return
    builder.open_main()
