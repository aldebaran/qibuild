## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Open a project with an IDE

"""
import os
import sys
import glob
import subprocess

from qibuild import ui
import qibuild

SUPPORTED_IDES = ["QtCreator", "Visual Studio", "Xcode"]

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")


def get_ide(qibuild_cfg):
    """ Return an IDE to use

    """
    known_ides = qibuild_cfg.ides.values()
    ide_names  = qibuild_cfg.ides.keys()
    if not known_ides:
        mess  =  "Could not find any IDE in configuration\n"
        mess +=  "Please use `qibuild config --wizard` or `qibuild config --edit`"
        raise Exception(mess)

    # Remove the one that are not supported:
    supported_ides = [x for x in known_ides if x.name in SUPPORTED_IDES]

    if len(supported_ides) == 1:
        return supported_ides[0]

    if not supported_ides:
        mess  = "Found those IDEs in configuration: %s\n" % ", ".join(ide_names)
        mess += "But `qibuild open` only supports: %s\n" % ", ".join(SUPPORTED_IDES)
        raise Exception(mess)

    #  User chose a specific config and an IDE matches this config
    if qibuild_cfg.ide:
        return qibuild_cfg.ide


    supported_names = [x.name for x in supported_ides]
    # Several IDEs, ask the user to choose
    ide_name = qibuild.interact.ask_choice(supported_names,
        "Please choose an ide to use")
    if not ide_name:
        return None
    return qibuild_cfg.ides[ide_name]



def do(args):
    """Main entry point """
    toc = qibuild.toc.toc_open(args.worktree, args)
    project = qibuild.cmdparse.project_from_args(toc, args)
    if not os.path.exists(project.build_directory):
        ui.error("""It looks like your project has not been configured yet
(The build directory: '%s' does not exists)""" %
        project.build_directory)
        answer = qibuild.interact.ask_yes_no(
            "Do you want me to run qibuild configure for you?",
            default=True)
        if not answer:
            sys.exit(2)
        else:
            args = [project.name]
            if toc.active_config:
              args.extend(["--config", toc.active_config])
            qibuild.run_action("qibuild.actions.configure", args)

    error_message = "Could not open project %s\n" % project.name
    qibuild_cfg = qibuild.config.QiBuildConfig(user_config=toc.active_config)
    qibuild_cfg.read()
    qibuild_cfg.read_local_config(toc.config_path)
    ide = get_ide(qibuild_cfg)
    if not ide:
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
    mess += "Supported IDES are: %s" % ", ".join(SUPPORTED_IDES)
    raise Exception(mess)
