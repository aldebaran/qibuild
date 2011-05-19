## Copyright (C) 2011 Aldebaran Robotics

"""Open a project with an IDE

"""
import os
import sys
import glob
import subprocess
import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")

def find_ide(toc):
    ides = list()
    vs        = False
    qtcreator = False
    xcode     = False


    qtcreator = toc.configstore.get("general", "env", "ide_path", default=False)
    if not qtcreator:
        qtcreator = qibuild.command.find_program("qtcreator")

    if sys.platform.startswith("win32"):
        vs = True
    if sys.platform == "darwin":
        xcode = True

    if xcode:
        ides.append("Xcode")
    if qtcreator:
        ides.append("QtCreator")
    if vs:
        ides.append("Visual Studio")
    return ides

def do(args):
    """Main entry point """
    toc      = qibuild.toc.toc_open(args.work_tree, args, use_env=True)
    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project

    project = toc.get_project(project_name)

    ides = find_ide(toc)
    return
    editor = toc.configstore.get("general", "env", "ide")
    if len(ides) == 1 and editor == None:
        editor = ides[0]
    if editor is None:
        editor  = qibuild.interact.ask_choice(ides, "Please choose between the following IDEs")
        qibuild.configstore.update_config(toc.user_config_path,
            "general", "env", "ide", editor)


    if editor == "Visual Studio":
        sln_files = glob.glob(project.build_directory + "/*.sln")
        assert len(sln_files) == 1, "Expecting only one sln, got %s" % sln_files
        subprocess.Popen(["start", sln_files[0]], shell=True)
        return

    if editor == "Xcode":
        projs = glob.glob(project.build_directory + "/*.xcodeproj")
        assert len(projs) == 1, "Expecting only one xcodeproj, got %s" % sln_files
        print "staring:", projs[0]
        subprocess.Popen(["open", projs[0]])

    if editor == "QtCreator":
        qtcreator_full_path = toc.configstore.get("general", "env", "ide_path", default = None)
        if not qtcreator_full_path:
            qtcreator = qibuild.command.find_program("qtcreator")
            if qtcreator is None:
                qtcreator_full_path = qibuild.interact.ask_program("Please enter path to qtcreator")
                # Store it so we dont ask again:
                qibuild.configstore.update_config(toc.user_config_path,
                    "general", "env", "ide_path", qtcreator_full_path)

        cmake_list = os.path.join(project.directory, "CMakeLists.txt")
        subprocess.Popen([qtcreator_full_path, cmake_list])
        return
