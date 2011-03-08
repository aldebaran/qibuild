## Copyright (C) 2011 Aldebaran Robotics

"""Open a project with an IDE

"""
import os
import glob
import subprocess

import qitools
import qibuild

KNOWN_IDES = ["QtCreator", "Visual Studio"]

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")

def do(args):
    """Main entry point """
    toc      = qibuild.toc.toc_open(args.work_tree, args, use_env=True)
    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project

    project = toc.get_project(project_name)

    editor = toc.configstore.get("general", "env", "ide")
    if editor is None:
        editor  = qitools.ask_choice(KNOWN_IDES, "Please choose between the following IDEs")
        qitools.configstore.update_config(toc.user_config_path,
            "general", "env", "ide", editor)

    if editor == "Visual Studio":
        sln_files = glob.glob(project.build_directory + "/*.sln")
        assert len(sln_files) == 1, "Expecting only one sln, got %s" % sln_files
        subprocess.Popen(["start", sln_files[0]])
        return

    if editor == "QtCreator":
        qitools.command.check_is_in_path("qtcreator")
        qtcreator = qitools.command.find_program("qtcreator")
        cmake_list = os.path.join(project.directory, "CMakeLists.txt")
        subprocess.Popen([qtcreator, cmake_list])
        return
