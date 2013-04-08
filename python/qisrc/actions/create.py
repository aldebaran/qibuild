## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Create a new project """

import os

from qisys import ui
import qisys.parsers
import qibuild.parsers

def copy_helper(project_name, directory):
    """Create a new project in the specified directory.

    """
    # Read the templates for projects
    template_dir = os.path.join(qisrc.QISRC_ROOT_DIR, "templates", "project")
    template_dir = os.path.abspath(template_dir)

    for file_name in os.listdir(template_dir):
        with open(os.path.join(template_dir, file_name), "r") as old_file:
            old_contents = old_file.read()
        new_contents = old_contents.replace("@project_name@", project_name)
        with open(os.path.join(directory, file_name), "w") as new_file:
            new_file.write(new_contents)

def configure_parser(parser):
    """Configure parser for this action """
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("project_name",
        help="The name of the project. "
             "The project will be created in QI_WORK_TREE/<name> ")
    parser.add_argument("--git", action="store_true",
        help="Create a git repository")


def do(args):
    """"Create a new project """
    build_worktree = qibuild.parsers.get_build_worktree(args)

    project_name = args.project_name
    project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        raise Exception("%s already exists" % project_path)
    os.mkdir(project_path)
    copy_helper(project_name, project_path)

    if args.git:
        qisys.command.call(["git", "init"], cwd=project_path)
        with open(os.path.join(project_path, ".gitignore"), "w") as fp:
            fp.write("build-*\n")
        qisys.command.call(["git" , "add" , "."], cwd=project_path)
        qisys.command.call(["git" , "commit" , "-m" , "initial commit"], cwd=project_path)

    ui.info(ui.green, "New project initialized in", ui.bold,  project_path)
    build_worktree.worktree.add_project(project_path)
    return build_worktree.get_build_project(project_name)
