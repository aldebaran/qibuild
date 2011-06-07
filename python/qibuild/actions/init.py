## Copyright (C) 2011 Aldebaran Robotics
"""Initialize a new toc worktree """


# FIXME qibuild --interactive:
#   - Propose a list of configs to choose from, automagically set
#     toolchain name and cmake generator.
#   (preparing the release of qitoolchain/ repo)
#   - Only configure the local file.

import os
import logging

import qibuild
import qitoolchain
import subprocess

LOGGER = logging.getLogger(__name__)



def ask_cmake_generator():
    """Ask the user to choose a cmake generator """
    out = ""
    try:
        cmake_process = subprocess.Popen(["cmake"], stdout=subprocess.PIPE)
        (out, _err) = cmake_process.communicate()
    except:
        cmake = qibuild.command.find_program("cmake.exe")
        if cmake:
            #TODO: ask user to enter one?
            raise Exception("Unable to guess cmake generators.")
        else:
            raise Exception("Could not find cmake. cmake should be in your PATH.")

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

    generator = qibuild.interact.ask_choice(generators, "Choose a CMake generator:")
    return generator


def ask_toolchain():
    """Ask the user to choose a toolchain name"""

    config_file = qitoolchain.get_tc_config_path()
    config = qibuild.configstore.ConfigStore()
    config.read(config_file)
    toolchain_names = qitoolchain.get_toolchain_names()
    return qibuild.interact.ask_choice(toolchain_names, "Choose a toolchain name")

def create_toolchain():
    """Ask the use for a toolchain name and create one"""
    print ":: Choose a toolchain name"
    answer = raw_input("> ")
    qibuild.cmdparse.run_action("qitoolchain.actions.create", [answer])
    return answer

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("--interactive", action="store_true",
        help="start a wizard to help you configuring qibuild")
    parser.add_argument("--force", action="store_true", help="force the init")

def do(args):
    """Main entry point"""
    work_tree = qibuild.qiworktree.worktree_from_args(args)
    build_cfg = qibuild.configstore.get_config_path()
    should_run = False
    if os.path.exists(build_cfg) and args.interactive:
        try:
            to_ask  = "%s already exists, do you which to configure it" % build_cfg
            should_run = qibuild.interact.ask_yes_no(to_ask)
        except KeyboardInterrupt:
            pass
    else:
        should_run = True

    if not should_run:
        return

    old_work_tree = qibuild.qiworktree.guess_work_tree(True)
    if old_work_tree and not args.force and not args.work_tree:
        print
        raise Exception("You already have a qi worktree in : %s.\n" % (old_work_tree) +
                        "If you know what you are doing and really want to create a new worktree here use --force.")

    qibuild.toc.create(work_tree, args)
    if not os.path.exists(build_cfg):
        template_cfg = os.path.join(qibuild.QIBUILD_ROOT_DIR, "templates", "qibuild.cfg")
        qibuild.sh.install(template_cfg, build_cfg)

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
    if qibuild.interact.ask_yes_no("Use a toolchain"):
        tc_config = qitoolchain.get_tc_config_path()
        if not os.path.exists(tc_config):
            if qibuild.interact.ask_yes_no("No toolchain found, create one"):
                toolchain_name = create_toolchain()
        else:
            toolchain_name = ask_toolchain()

    qibuild.configstore.update_config(build_cfg, "build", "cmake_generator", cmake_generator)
    qibuild.configstore.update_config(build_cfg, "build", "toolchain", toolchain_name)
