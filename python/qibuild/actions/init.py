## Copyright (C) 2011 Aldebaran Robotics
"""Initialize a new toc worktree """

import os
import logging

import qibuild
import qitoolchain
import qitools
import qitools.cmdparse
import subprocess

LOGGER = logging.getLogger(__name__)


def ask_cmake_generator():
    """Ask the user to choose a cmake generator """
    cmake_process = subprocess.Popen(["cmake"], stdout=subprocess.PIPE)
    (out, _err) = cmake_process.communicate()
    lines = out.splitlines()
    interesting_lines = list()
    interesting = False
    for line in lines:
        if line == "Generators":
            interesting = True
            continue
        if interesting and line:
           interesting_lines.append(line)

    generators = list()
    for line in interesting_lines:
        if " = " in line:
            generator = line.split("=")[0]
            generator = generator.strip()
            if generator:
                generators.append(generator)

    generator = qitools.ask_choice(generators, "Choose a CMake generator:")
    return generator


def ask_toolchain():
    """Ask the user to choose a toolchain name"""

    config_file = qitoolchain.get_tc_config_path()
    config = qitools.configstore.ConfigStore()
    config.read(config_file)
    toolchain_dict = config.get("toolchain", default=dict())
    toolchain_names = toolchain_dict.keys()
    return qitools.ask_choice(toolchain_names, "Choose a toolchain name")

def create_toolchain():
    """Ask the use for a toolchain name and create one"""
    print ":: Choose a toolchain name"
    answer = raw_input("> ")
    qitools.run_action("qitoolchain.actions.create", [answer])
    return answer

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("--interactive", action="store_true",
        help="start a wizard to help you configuring qibuild")

def do(args):
    """Main entry point"""
    work_tree = qitools.qiworktree.worktree_from_args(args)
    build_cfg = qitools.qiworktree.get_user_config_path()
    should_run = False
    if os.path.exists(build_cfg):
        if not args.interactive:
            LOGGER.error("%s already exists, aborting", build_cfg)
            return
        try:
            to_ask  = "%s already exists, do you which to configure it" % build_cfg
            should_run = qitools.ask_yes_no(to_ask)
        except KeyboardInterrupt:
            pass
    else:
        should_run = True

    if not should_run:
        return

    qibuild.toc.create(work_tree, args)

    if not args.interactive:
        return

    try:
        run_wizard(build_cfg)
    except KeyboardInterrupt:
        pass

def run_wizard(build_cfg):
    """Write a new configuration if the file passed as
    argument, asking the user a few questions

    """
    cmake_generator = ask_cmake_generator()

    toolchain_name = None
    if qitools.ask_yes_no("Use a toolchain"):
        tc_config = qitoolchain.get_tc_config_path()
        if not os.path.exists(tc_config):
            if qitools.ask_yes_no("No toolchain found, create one"):
                toolchain_name = create_toolchain()
        else:
            toolchain_name = ask_toolchain()

    qitools.configstore.update_config(build_cfg,
        "general", "build", "cmake_generator", cmake_generator)
    qitools.configstore.update_config(build_cfg,
        "general", "build", "toolchain", toolchain_name)
