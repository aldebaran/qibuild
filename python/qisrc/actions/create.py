## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Create a new project """

import os

import qisrc # for QISRC_ROOT_DIR
from qisys import ui
import qisys.parsers
import qisrc.templates

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("project_name",
        help="The name of the project. "
             "The project will be created in QI_WORK_TREE/<name> ")
    parser.add_argument("-i", "--input", "--template-path", dest="template_path")
    parser.add_argument("--git", action="store_true",
        help="Create a git repository")
    parser.add_argument("-o", "--output", dest="output_dir")

def do(args):
    """"Create a new project """
    try:
        worktree = qisys.parsers.get_worktree(args)
    except qisys.worktree.NotInWorkTree:
        worktree = None

    project_name = os.path.basename(args.project_name)

    output_dir = args.output_dir
    if not output_dir:
        output_dir = qisrc.templates.attached_lower(project_name)
        output_dir = os.path.join(os.getcwd(), output_dir)

    if os.path.exists(output_dir):
        raise Exception("%s already exists" % output_dir)

    template_path = args.template_path
    if not template_path:
        template_path = os.path.join(qisrc.QISRC_ROOT_DIR, "templates", "project")

    qisrc.templates.process(template_path, output_dir, project_name=project_name)

    if args.git:
        qisys.command.call(["git", "init"], cwd=output_dir)
        with open(os.path.join(output_dir, ".gitignore"), "w") as fp:
            fp.write("build-*\n")
        qisys.command.call(["git" , "add" , "."], cwd=output_dir)
        qisys.command.call(["git" , "commit" , "-m" , "initial commit"], cwd=output_dir)

    ui.info(ui.green, "New project initialized in", ui.bold,  output_dir)
    if worktree:
        worktree.add_project(output_dir)
        return worktree.get_project(output_dir)
