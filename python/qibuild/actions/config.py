## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Display the current config """

import os
import sys
import subprocess

import qibuild
import qitoolchain

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("--edit", action="store_true",
        help="edit the configuration")
    parser.add_argument("--wizard", action="store_true",
        help="run a wizard to edit the configuration")

def do(args):
    """Main entry point"""
    toc = None
    try:
        toc = qibuild.toc.toc_open(args.work_tree, args)
    except qibuild.toc.TocException:
        pass

    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()

    if args.wizard:
        run_config_wizard(toc)
        return

    if args.edit:
        editor = qibuild_cfg.defaults.env.editor
        if not editor:
            editor = os.environ.get("VISUAL")
        if not editor:
            editor = os.environ.get("EDITOR")
        if not editor:
            # Ask the user to choose, and store the answer so
            # that we never ask again
            print "Could not find the editor to use."
            editor = qibuild.interact.ask_program("Please enter an editor")
            qibuild_cfg.defaults.env.editor = editor
            qibuild_cfg.write()

        full_path = qibuild.command.find_program(editor)
        subprocess.call([full_path, qibuild.config.QIBUILD_CFG_PATH])
        return

    if not toc:
        print qibuild_cfg
        return

    print "General configuration"
    print "---------------------"
    print qibuild.config.indent(str(toc.config))
    print

    print "Local configuration"
    print "-------------------"
    print qibuild.config.indent(str(toc.config.local))

    print
    print "Projects configuration"
    print "----------------------"
    projects = toc.projects
    if projects:
        print "  Projects:"
        for project in projects:
            print qibuild.config.indent(str(project.config), 2)


def get_build_env(qibuild_cfg):
    """ Return the build environnment as read from
    qibuild config

    """
    envsetter = qibuild.envsetter.EnvSetter()
    envsetter.read_config(qibuild_cfg)
    return envsetter.get_build_env()


def guess_cmake(qibuild_cfg):
    """ Try to find cmake

    """
    build_env = get_build_env(qibuild_cfg)
    cmake = qibuild.command.find_program("cmake", env=build_env)
    if sys.platform.startswith("win"):
        # FIXME: loook for it in registry
        pass
    if sys.platform.startswith("darwin"):
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

def guess_cmake_generators(cmake):
    """ Use cmake --help to get the list of cmake
    generators

    """
    process = subprocess.Popen([cmake, "--help"],
        stdout=subprocess.PIPE)
    (out, err) = process.communicate()
    intersting = False
    intersting_lines = list()
    magic_line = "The following generators are available on this platform:"
    # pylint: disable-msg=E1103
    for line in out.splitlines():
        if line == magic_line:
            intersting = True
            continue
        if intersting:
            intersting_lines.append(line)
    to_parse = ""
    for line in intersting_lines:
        to_parse += line.strip()
        if "=" in line:
            to_parse += "\n"
    res = list()
    for line in to_parse.splitlines():
        generator = line.split("=")[0]
        res.append(generator.strip())
    return res

def ask_cmake_generator(cmake):
    """ Ask the user to choose a cmake generator

    """
    cmake_generators = guess_cmake_generators(cmake)
    cmake_generator = qibuild.interact.ask_choice(cmake_generators,
        "Please choose a generator")

    return cmake_generator

def ask_ide(qibuild_cfg):
    """ Ask the user to choose an IDE

    """
    ides = ["QtCreator", "Eclipse CDT"]
    if sys.platform.startswith("win32"):
        ides.append("Visual Studio")
    if sys.platform == "darwin":
        ides.append("Xcode")
    ide = qibuild.interact.ask_choice(ides,
        "Please choose an IDE")
    return ide


def configure_qtcreator(qibuild_cfg):
    """ Configure QtCreator

    """
    ide = qibuild.config.IDE()
    ide.name = "QtCreator"
    build_env = get_build_env(qibuild_cfg)
    qtcreator_path = qibuild.command.find_program("qtcreator", env=build_env)
    if qtcreator_path:
        print "Found QtCreator: ", qtcreator_path
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

def configure_local_settings(qibuild_cfg, toc):
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
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()

    # Ask for a default cmake generator
    cmake = guess_cmake(qibuild_cfg)
    generator = ask_cmake_generator(cmake)
    qibuild_cfg.defaults.cmake.generator = generator

    ide = ask_ide(qibuild_cfg)
    if ide:
        configure_ide(qibuild_cfg, ide)

    qibuild_cfg.write()

    if toc:
        configure_local_settings(qibuild_cfg, toc)
