"""Create a new project """

import os
import shutil
import logging
import qitools


LOGGER = logging.getLogger(__name__)

def copy_helper(project_name, directory):
    """Create a new project in the specified directory.

    """
    cur_dir = os.path.dirname(os.path.abspath(__file__))

    # Read the templates for projects
    template_dir = os.path.join(cur_dir, "..", "templates", "project")
    template_dir = os.path.abspath(template_dir)

    for file in os.listdir(template_dir):
        with open(os.path.join(template_dir, file), "r") as old_file:
            old_contents = old_file.read()
        new_contents = old_contents.replace("@project_name@", project_name)
        with open(os.path.join(directory, file), "w") as new_file:
            new_file.write(new_contents)

    # Also create the necessary qibuild.cmake file:
    qibuild_cmake = os.path.join(cur_dir, "..", "..", "..",
        "cmake", "qibuild", "templates", "qibuild.cmake")
    qibuild_cmake = os.path.abspath(qibuild_cmake)

    shutil.copy(qibuild_cmake, os.path.join(directory, "qibuild.cmake"))


def configure_parser(parser):
    """Configure parser for this action """
    qitools.cmdparse.default_parser(parser)
    parser.add_argument("project_path", help="either the name of the project, or  "
        "a new path for the project")


def do(args):
    """"Create a new project """
    project_path = qitools.sh.to_native_path(args.project_path)
    project_name = os.path.basename(project_path)
    if os.path.exists(project_path):
        raise Exception("%s already exists" % project_path)
    os.mkdir(project_path)
    copy_helper(project_name, project_path)

    LOGGER.info("New project initialized in %s", project_path)

