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


def get_qtcreator_path(toc):
    """ Get the path to qtcreator

    """
    qtcreator_path = None
    # Get it from conf:
    qtcreator_conf = toc.configstore.ides.get("QtCreator")
    if qtcreator_conf:
        qtcreator_path = qtcreator_conf.path
        if os.path.exists(qtcreator_path):
            return qtcreator_path
        else:
            mess  = "Invalide configuration detected\n"
            mess += "In %s\n" % toc.config_path
            mess += "ide.qtcreator.path is %s\n" % qtcreator_conf
            mess += "but this file does not exist\n"
            mess += "Please fix your configuration"
            raise Exception(mess)

    # Try to guess it:
    build_env = toc.envsetter.get_build_env()
    qtcreator_path = qibuild.command.find_program("qtcreator", env=build_env)
    if qtcreator_path:
        return qtcreator_path
    mac_path = "/Applications/Qt Creator.app/Contents/MacOS/Qt Creator"
    if os.path.exists(mac_path):
        return mac_path
    qtcreator_path = qibuild.interact.ask_program("Please enter path to qtcreator")
    return qtcreator_path

def find_ide(toc):
    """ Return a ide to use.

    - Either read it from configuration
    - Or ask it to the user, but use sys.platform
      to ask only reasonable choices

    Return the path to the chosen ide, and
    store in it the configuration to not
    ask it again

    """
    ide = toc.configstore.ide
    if ide:
        return ide
    ides = ["QtCreator"] # QtCreator rocks!
    # FIXME: add 'Eclipse CDT'
    if sys.platform.startswith("win32"):
        ides.append("Visual Studio")

    if sys.platform == "darwin":
        ides.append("Xcode")

    if ide is None:
        ide_config = qibuild.config.IDE()
        if len(ides) > 1:
            ide  = qibuild.interact.ask_choice(ides,
                "Please choose between the following IDEs")
        else:
            ide = "QtCreator"
        if  ide == "QtCreator":
            ide_path = get_qtcreator_path(toc)
            if ide_path:
                ide_config.path = ide_path
        ide_config.name = ide
        toc.configstore.add_ide(ide_config)
        if len(toc.configstore.ides) == 1:
            toc.configstore.set_default_ide(ide)
            toc.ide = ide
    toc.save_config()
    return ide_config


def do(args):
    """Main entry point """
    toc      = qibuild.toc.toc_open(args.work_tree, args)
    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project

    project = toc.get_project(project_name)

    error_message = "Could not open project %s\n" % project_name

    ide = find_ide(toc)
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
        cmake_list = os.path.join(project.directory, "CMakeLists.txt")
        print "starting QtCreator:"
        print ide_path, cmake_list
        subprocess.Popen([ide_path, cmake_list])
        return

    # Not supported (yet) IDE:
    mess  = "Invalid ide: %s\n" % ide.name
    mess += "Supported IDES are: QtCreator, Visual Studio, XCode"
    raise Exception(mess)
