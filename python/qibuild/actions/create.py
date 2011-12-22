## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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

    # Also create the necessary qibuild.cmake file:
    to_copy = os.path.join(qibuild.get_cmake_qibuild_dir(),
        "qibuild", "templates", "qibuild.cmake")
    shutil.copy(to_copy, os.path.join(directory, "qibuild.cmake"))


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)
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
    try:
        qiwt = qibuild.worktree_open(args.work_tree)
    except qibuild.worktree.WorkTreeException:
        if qibuild.interact.ask_yes_no("Warning, no worktree found. Create one"):
            qibuild.run_action("qibuild.actions.init", ["--interactive"])
            qiwt = qibuild.worktree_open(args.work_tree)

    project_name = args.project_name
    if qiwt:
        project_path = os.path.join(qiwt.work_tree, project_name)
    else:
        project_path = os.path.join(os.getcwd(), project_name)

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


