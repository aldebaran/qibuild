## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" qibuild wizard

"""

import os

import qibuild
import qitoolchain

def guess_cmake(qibuild_cfg):
    """ Try to find cmake

    """
    build_env = qibuild.config.get_build_env()
    cmake = qibuild.command.find_program("cmake", env=build_env)
    platform = qibuild.get_platform()
    if platform == "windows":
        # FIXME: loook for it in registry
        pass
    if platform == "mac":
        # FIXME: hard-code some path in /Applications
        pass

    if cmake:
        print "Found CMake:" , cmake
        return cmake

    print "CMake not found"
    cmake = qibuild.interact.ask_program("Please enter full CMake path")
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
    cmake_generator = qibuild.interact.ask_choice(cmake_generators,
        "Please choose a generator")

    return cmake_generator

def ask_ide(qibuild_cfg):
    """ Ask the user to choose an IDE

    """
    ides = ["QtCreator", "Eclipse CDT"]
    platform = qibuild.get_platform()
    if platform == "windows":
        ides.append("Visual Studio")
    if platform == "mac":
        ides.append("Xcode")
    ide = qibuild.interact.ask_choice(ides,
        "Please choose an IDE")
    return ide


def configure_qtcreator(qibuild_cfg):
    """ Configure QtCreator

    """
    ide = qibuild.config.IDE()
    ide.name = "QtCreator"
    build_env = qibuild.config.get_build_env()
    qtcreator_path = qibuild.command.find_program("qtcreator", env=build_env)
    if qtcreator_path:
        print "Found QtCreator: ", qtcreator_path
        mess  = "Do you want to use qtcreator from %s ?\n" % qtcreator_path
        mess += "Answer 'no' if you installed qtcreator from Nokia's installer"
        answer = qibuild.interact.ask_yes_no(mess, default=True)
        if not answer:
            qtcreator_path = None
    else:
        print "QtCreator NOT found"
    if not qtcreator_path:
        qtcreator_path = qibuild.interact.ask_program(
            "Please enter full qtcreator path")
    if not qtcreator_path:
        print "Not adding config for QtCreator"
        print "qibuild open will not work"
        return
    ide.path = qtcreator_path
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

def configure_local_settings(toc):
    """ Configure local settings for this worktree

    """
    print
    print "Found a worktree in", toc.work_tree
    answer = qibuild.interact.ask_yes_no(
        "Do you want to configure settings for this worktree",
        default=True)
    if not answer:
        return
    tc_names = qitoolchain.get_tc_names()
    if tc_names:
        print "Found the following toolchains: ", ", ".join(tc_names)
        answer = qibuild.interact.ask_yes_no(
            "Use one of these toolchains by default",
            default=True)
        if answer:
            default = qibuild.interact.ask_choice(tc_names,
                "Choose a toolchain to use by default")
            if default:
                toc.config.local.defaults.config = default
                toc.save_config()
    answer = qibuild.interact.ask_yes_no(
        "Do you want to use a unique build dir "
        "(mandatory when using Eclipse)",
        default=False)

    build_dir = None
    if answer:
        build_dir = qibuild.interact.ask_string("Path to a build directory")
        build_dir = os.path.expanduser(build_dir)
        full_path = os.path.join(toc.work_tree, build_dir)
        print "Will use", full_path, "as a root for all build directories"
    if build_dir:
        toc.config.local.build.build_dir = build_dir
        toc.save_config()

    sdk_dir = None
    answer = qibuild.interact.ask_yes_no(
        "Do you want to use a unique SDK dir",
        default=False)
    if answer:
        sdk_dir = qibuild.interact.ask_string("Path to a SDK directory")
        sdk_dir = os.path.expanduser(sdk_dir)
        full_path = os.path.join(toc.work_tree, sdk_dir)
        print "Will use", full_path, "as a unique SDK directory"
    if sdk_dir:
        toc.config.local.build.sdk_dir = sdk_dir
        toc.save_config()


def run_config_wizard(toc):
    """ Run a nice interactive config wizard

    """
    if toc:
        qibuild_cfg = toc.config
    else:
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg_path = qibuild.config.get_global_cfg_path()
        if not os.path.exists(qibuild_cfg_path):
            to_create = os.path.dirname(qibuild_cfg_path)
            qibuild.sh.mkdir(to_create, recursive=True)
            with open(qibuild_cfg_path, "w") as fp:
                fp.write('<qibuild version="1" />\n')
        qibuild_cfg.read()

    # Ask for a default cmake generator
    guess_cmake(qibuild_cfg)
    generator = ask_cmake_generator()
    qibuild_cfg.defaults.cmake.generator = generator

    ide = ask_ide(qibuild_cfg)
    if ide:
        configure_ide(qibuild_cfg, ide)

    qibuild_cfg.write()

    if toc:
        configure_local_settings(toc)
