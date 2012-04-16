## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Create a new project """

import os
import shutil
import logging
import qibuild


LOGGER = logging.getLogger(__name__)

def copy_helper(project_name, directory):
    """Create a new project in the specified directory.

    """
    # Read the templates for projects
    template_dir = os.path.join(qibuild.QIBUILD_ROOT_DIR, "templates", "project")
    template_dir = os.path.abspath(template_dir)

    for file_name in os.listdir(template_dir):
        with open(os.path.join(template_dir, file_name), "r") as old_file:
            old_contents = old_file.read()
        new_contents = old_contents.replace("@project_name@", project_name)
        with open(os.path.join(directory, file_name), "w") as new_file:
            new_file.write(new_contents)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("project_name",
        help="The name of the project. "
             "The project will be created in QI_WORK_TREE/<name> ")
    parser.add_argument("--git", action="store_true",
        help="Create a git repository")


def do(args):
    """"Create a new project """
    # Try to open a worktree.
    # If not, ask the user if he wants to create one:
    qiwt = None
    qiwt = qibuild.open_worktree(args.worktree)

    project_name = args.project_name
    project_path = os.path.join(qiwt.root, project_name)

    if os.path.exists(project_path):
        raise Exception("%s already exists" % project_path)
    os.mkdir(project_path)
    copy_helper(project_name, project_path)


    if args.git:
        qibuild.command.call(["git", "init"], cwd=project_path)
        with open(os.path.join(project_path, ".gitignore"), "w") as fp:
            fp.write("build-*\n")
        qibuild.command.call(["git" , "add" , "."], cwd=project_path)
        qibuild.command.call(["git" , "commit" , "-m" , "initial commit"], cwd=project_path)

    LOGGER.info("New project initialized in %s", project_path)
    qiwt.add_project(project_name, src=project_path)
