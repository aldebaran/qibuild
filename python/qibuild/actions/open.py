## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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


def get_ide(toc):
    """ Return an IDE to use

    """
    qibuild_cfg = qibuild.config.QiBuildConfig(user_config=toc.active_config)
    qibuild_cfg.read()
    ide = qibuild_cfg.ide
    return ide


def do(args):
    """Main entry point """
    toc      = qibuild.toc.toc_open(args.work_tree, args)
    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project

    project = toc.get_project(project_name)

    error_message = "Could not open project %s\n" % project_name
    ide = get_ide(toc)
    if not ide:
        print "Could not find any IDE in configuration"
        print "Please use `qibuild config --wizard` or `qibuild config --edit`"
        return

    if ide.name == "Visual Studio":
        sln_files = glob.glob(project.build_directory + "/*.sln")
        if len(sln_files) != 1:
            raise Exception(error_message + "Expecting only one sln, got %s" % sln_files)
        print "starting VisualStudio:"
        print "%s %s" % ("start", sln_files[0])
        subprocess.Popen(["start", sln_files[0]], shell=True)
        return

    if ide.name == "Xcode":
        projs = glob.glob(project.build_directory + "/*.xcodeproj")
        if len(projs) == 0:
            raise Exception(error_message +
                "Do you have called qibuild configure with --cmake-generator=Xcode?")
        if len(projs) > 1:
            raise Exception(error_message +
                "Expecting only one xcode project file, got %s" % projs)
        print "starting Xcode:"
        print "%s %s" % ("open", projs[0])
        subprocess.Popen(["open", projs[0]])
        return

    if ide.name == "QtCreator":
        ide_path = ide.path
        if not ide_path:
            ide_path = 'qtcreator'
        cmake_list = os.path.join(project.directory, "CMakeLists.txt")
        if not os.access(ide_path, os.X_OK):
            mess  = "Invalid configuration dectected!\n"
            mess += "QtCreator path (%s) is not a valid path\n" % ide_path
            mess += "Please run `qibuild config --wizard\n"
            raise Exception(mess)
        print "starting QtCreator:"
        print ide_path, cmake_list
        subprocess.Popen([ide_path, cmake_list])
        return

    # Not supported (yet) IDE:
    mess  = "Invalid ide: %s\n" % ide.name
    mess += "Supported IDES are: QtCreator, Visual Studio, XCode"
    raise Exception(mess)
