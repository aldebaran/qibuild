## Copyright (C) 2011 Aldebaran Robotics
"""Create a new project """

import os
import shutil
import logging
import qibuild
import qibuild


LOGGER = logging.getLogger(__name__)

def copy_helper(project_name, directory):
    """Create a new project in the specified directory.

    """
    # Read the templates for projects
    template_dir = os.path.join(qibuild.QIBUILD_ROOT_DIR, "templates", "project")
    template_dir = os.path.abspath(template_dir)

    for file in os.listdir(template_dir):
        with open(os.path.join(template_dir, file), "r") as old_file:
            old_contents = old_file.read()
        new_contents = old_contents.replace("@project_name@", project_name)
        with open(os.path.join(directory, file), "w") as new_file:
            new_file.write(new_contents)

    # Also create the necessary qibuild.cmake file:
    to_copy = os.path.join(qibuild.CMAKE_QIBUILD_DIR, "templates", "qibuild.cmake")
    shutil.copy(to_copy, os.path.join(directory, "qibuild.cmake"))


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.qiworktree.work_tree_parser(parser)
    parser.add_argument("project_name",
        help="The name of the project. "
             "The project will be created in QI_WORK_TREE/<name> ")


def do(args):
    """"Create a new project """
    # Try to open a qiworktree.
    # If not, ask the user if he wants to create one:
    qiwt = None
    try:
        qiwt = qibuild.qiworktree_open(args.work_tree)
    except qibuild.qiworktree.WorkTreeException:
        if qibuild.interact.ask_yes_no("Warning, no worktree found. Create one"):
            qibuild.run_action("qibuild.actions.init", ["--interactive"])
            qiwt = qibuild.qiworktree_open(args.work_tree)

    project_name = args.project_name
    if qiwt:
        project_path = os.path.join(qiwt.work_tree, project_name)
    else:
        project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        raise Exception("%s already exists" % project_path)
    os.mkdir(project_path)
    copy_helper(project_name, project_path)

    LOGGER.info("New project initialized in %s", project_path)


