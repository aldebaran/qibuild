## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Open a project with an IDE

"""
import os
import sys
import glob
import subprocess

from qisys import ui
import qisys
import qisys.error
import qibuild.parsers

SUPPORTED_IDES = ["QtCreator", "Visual Studio", "Xcode"]

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)

def do(args):
    """Main entry point."""
    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    if len(cmake_builder.projects) != 1:
        ui.fatal("This action can only work on one project")
    project = cmake_builder.projects[0]
    if not os.path.exists(project.build_directory):
        ui.error("""It looks like your project has not been configured yet
(The build directory: '%s' does not exist)""" %
        project.build_directory)
        answer = qisys.interact.ask_yes_no(
            "Do you want me to run qibuild configure for you?",
            default=True)
        if not answer:
            sys.exit(2)
        else:
            cmake_builder.configure()

    ide = get_ide(cmake_builder.build_config.qibuild_cfg)
    if not ide:
        return

    if ide.name == "Visual Studio":
        open_visual(project)
    elif ide.name == "Xcode":
        open_xcode(project)
    elif ide.name == "QtCreator":
        open_qtcreator(project, ide.path)
    else:
        # Not supported (yet) IDE:
        mess  = "Invalid ide: %s\n" % ide.name
        mess += "Supported IDES are: %s" % ", ".join(SUPPORTED_IDES)
        ui.fatal(mess)


def get_ide(qibuild_cfg):
    """Return an IDE to use."""
    known_ides = qibuild_cfg.ides.values()
    ide_names  = qibuild_cfg.ides.keys()
    if not known_ides:
        ui.warning("No IDE configured yet")
        ui.info("Tips: use `qibuild config --wizard` to configure an IDE")
        return None

    # Remove the one that are not supported:
    supported_ides = [x for x in known_ides if x.name in SUPPORTED_IDES]

    if len(supported_ides) == 1:
        return supported_ides[0]

    if not supported_ides:
        mess  = "Found those IDEs in configuration: %s\n" % ", ".join(ide_names)
        mess += "But `qibuild open` only supports: %s\n" % ", ".join(SUPPORTED_IDES)
        ui.fatal(mess)

    #  User chose a specific config and an IDE matches this config
    if qibuild_cfg.ide:
        return qibuild_cfg.ide


    supported_names = [x.name for x in supported_ides]
    # Several IDEs, ask the user to choose
    ide_name = qisys.interact.ask_choice(supported_names,
        "Please choose an IDE to use")
    if not ide_name:
        return None
    return qibuild_cfg.ides[ide_name]



def open_visual(project):
    sln_files = glob.glob(project.build_directory + "/*.sln")
    if not sln_files:
        raise OpenError(project, "No .sln file found\n"
                        "Please make sure you are using a Visual Studio generator")
    elif len(sln_files) > 1:
        raise OpenError(project, "Expecting only one sln, got %s" % sln_files)

    print "starting VisualStudio:"
    print "%s %s" % ("start", sln_files[0])
    subprocess.Popen(["start", sln_files[0]], shell=True)

def open_xcode(project):
    projs = glob.glob(project.build_directory + "/*.xcodeproj")
    if not projs:
        raise OpenError(project, "No .xcodeproj directory found\n")
    elif len(projs) > 1:
        raise OpenError(project, "Expecting only one xcode project file, "
                                 "got %s" % projs)
    print "starting Xcode:"
    print "%s %s" % ("open", projs[0])
    subprocess.Popen(["open", projs[0]])

def open_qtcreator(project, qtcreator_path=None):
    if not qtcreator_path:
        qtcreator_path = qisys.command.find_program("qtcreator")
    cmake_list = os.path.join(project.path, "CMakeLists.txt")
    if not qtcreator_path or not os.path.exists(qtcreator_path):
        raise OpenError(project,
                        "QtCreator path not configured properly\n"
                        "Please run `qibuild config --wizard")
    print "starting QtCreator:"
    if qtcreator_path.endswith((".app", ".app/")):
        cmd = ["open", "-a", qtcreator_path, cmake_list]
    else:
        cmd = [qtcreator_path, cmake_list]
    print " ".join(cmd)
    subprocess.Popen(cmd)


class OpenError(qisys.error.Error):
    def __init__(self, project, reason):
        self.project = project
        self.reason = reason

    def __str__(self):
        res = """ \
Could not open {project.name}
{reason}
"""
        return res.format(project=self.project, reason=self.reason)
