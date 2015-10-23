## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" qibuild wizard

"""

import os
import sys

from qisys import ui
import qisys
import qibuild
import qitoolchain

def guess_cmake(qibuild_cfg):
    """ Try to find cmake

    """
    # FIXME: loook for it in registry on windows
    # FIXME: look for it in /Applications on mac
    build_env = qibuild.config.get_build_env()
    cmake = qisys.command.find_program("cmake", env=build_env)
    if cmake:
        print "Found CMake:" , cmake
        return cmake
    print "CMake not found"
    cmake = qisys.interact.ask_program("Please enter full CMake path")
    if not cmake:
        raise Exception("qiBuild cannot work without CMake\n"
            "Please install CMake if necessary and re-run this wizard\n")
    # Add path to CMake in build env
    cmake_path = os.path.dirname(cmake)
    qibuild_cfg.add_to_default_path(cmake_path)
    qibuild_cfg.write()
    return cmake

def ask_cmake_generator():
    """ Ask the user to choose a cmake generator

    """
    cmake_generators = qibuild.cmake.get_known_cmake_generators()
    cmake_generator = qisys.interact.ask_choice(cmake_generators,
        "Please choose a generator")

    return cmake_generator

def ask_ide():
    """ Ask the user to choose an IDE

    """
    ides = ["None", "QtCreator", "Eclipse CDT"]
    if sys.platform.startswith("win"):
        ides.append("Visual Studio")
    if sys.platform == "darwin":
        ides.append("Xcode")
    ide = qisys.interact.ask_choice(ides,
        "Please choose an IDE")
    if ide is "None":
        return None
    return ide

def configure_qtcreator(qibuild_cfg):
    """ Configure QtCreator

    """
    if sys.platform == "darwin":
        _configure_qtcreator_mac(qibuild_cfg)
    else:
        _configure_qtcreator(qibuild_cfg)

def _configure_qtcreator(qibuild_cfg):
    """ Helper for configure_qtcreator on Linux and Windows """
    ide = qibuild.config.IDE()
    ide.name = "QtCreator"
    build_env = qibuild.config.get_build_env()
    qtcreator_path = qisys.command.find_program("qtcreator", env=build_env)
    if qtcreator_path:
        ui.info(ui.green, "::", ui.reset,  "Found QtCreator:", qtcreator_path)
        mess  = "Do you want to use qtcreator from %s?\n" % qtcreator_path
        mess += "Answer 'no' if you installed qtcreator from Nokia's installer"
        answer = qisys.interact.ask_yes_no(mess, default=True)
        if not answer:
            qtcreator_path = None
    else:
        ui.warning("QtCreator not found")
    if not qtcreator_path:
        qtcreator_path = qisys.interact.ask_program(
            "Please enter full qtcreator path")
    if not qtcreator_path:
        ui.warning("Not adding config for QtCreator",
                   "qibuild open will not work", sep="\n")
        return
    ide.path = qtcreator_path
    qibuild_cfg.add_ide(ide)

def _configure_qtcreator_mac(qibuild_cfg):
    ide = qibuild.config.IDE()
    ide.name = "QtCreator"
    default_path = "/Applications/Qt Creator.app/"
    if os.path.exists(default_path):
        qtcreator_app_path = default_path
    else:
        ui.info("QtCreator.app not found in /Applications")
        qtcreator_app_path = qisys.interact.ask_app("Please enter QtCreator app path")
    if not qtcreator_app_path:
        ui.warning("Not adding config for QtCreator",
                   "qibuild open will not work", sep="\n")
        return
    ide.path = qtcreator_app_path
    qibuild_cfg.add_ide(ide)


def configure_ide(qibuild_cfg, ide_name):
    """ Configure an IDE

    """
    if ide_name == "QtCreator":
        configure_qtcreator(qibuild_cfg)
        return
    ide = qibuild.config.IDE()
    ide.name = ide_name
    qibuild_cfg.add_ide(ide)

def configure_local_settings(build_worktree):
    """ Configure local settings for this worktree

    """
    print
    worktree_root = build_worktree.root
    ui.info(ui.green, "::", ui.reset,  "Found a worktree in", worktree_root)
    qibuild_cfg = build_worktree.qibuild_cfg
    answer = qisys.interact.ask_yes_no(
        "Do you want to configure settings for this worktree?",
        default=False)
    if not answer:
        return
    config_names = qibuild.config.get_config_names()
    if config_names:
        ui.info(ui.green, "::", ui.reset,
                "Found the following build configs: ", ", ".join(config_names))
        answer = qisys.interact.ask_yes_no(
            "Use one of these build configs by default",
            default=True)
        if answer:
            default = qisys.interact.ask_choice(config_names,
                "Choose a build config to use by default")
            if default:
                qibuild_cfg.local.defaults.config = default
                qibuild_cfg.write_local_config(build_worktree.qibuild_xml)
    answer = qisys.interact.ask_yes_no(
        "Do you want to use a unique build dir?"
        " (mandatory when using Eclipse)",
        default=False)

    build_prefix = None
    if answer:
        build_prefix = qisys.interact.ask_string("Path to a build directory")
        build_prefix = os.path.expanduser(build_prefix)
        full_path = os.path.join(worktree_root, build_prefix)
        ui.info(ui.green, "::", ui.reset,
                "Will use", full_path, "as a root for all build directories")
    qibuild_cfg.local.build.prefix = build_prefix
    qibuild_cfg.write_local_config(build_worktree.qibuild_xml)



def run_config_wizard(build_worktree=None):
    """ Run a nice interactive config wizard

    """
    if build_worktree:
        qibuild_cfg = build_worktree.qibuild_cfg
    else:
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg_path = qibuild.config.get_global_cfg_path()
        if not os.path.exists(qibuild_cfg_path):
            to_create = os.path.dirname(qibuild_cfg_path)
            qisys.sh.mkdir(to_create, recursive=True)
            with open(qibuild_cfg_path, "w") as fp:
                fp.write('<qibuild version="1" />\n')
        qibuild_cfg.read()

    # Ask for a default cmake generator
    guess_cmake(qibuild_cfg)
    generator = ask_cmake_generator()
    qibuild_cfg.defaults.cmake.generator = generator

    ide = ask_ide()
    if ide:
        configure_ide(qibuild_cfg, ide)

    qibuild_cfg.write()

    if build_worktree:
        configure_local_settings(build_worktree)
