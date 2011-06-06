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

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.qiworktree.work_tree_parser(parser)
    parser.add_argument("--interactive", action="store_true",
        help="start a wizard to help you configuring qibuild")
    parser.add_argument("--force", action="store_true", help="force the init")

def do(args):
    """Main entry point"""
    # If user did not specify a worktree, make sure he is not
    # trying to create nested worktrees (there's nothing wrong in
    # having nested worktree, but it may be confusing a little bit)
    if not args.work_tree:
        old_work_tree = qibuild.qiworktree.guess_work_tree()
        if old_work_tree and os.path.exists(old_work_tree) and not args.force:
            raise Exception("You already have a qi worktree in : %s.\n" % (old_work_tree) +
                        "Use --force if you know what you are doing "
                        "and really want to create a new worktree here.")

    # Use getcwd() if no worktree was given
    work_tree = args.work_tree
    if not work_tree:
        work_tree = os.getcwd()

    # Safe to be called: only creates the .qi/ repertory
    # if it does not exists.
    qibuild.toc.create(work_tree)

    # Safe to be called now that we've created it :)
    toc = qibuild.toc.toc_open(work_tree)

    if not args.interactive:
        return

    run_wizard(toc)


def ask_config(toc):
    """ Ask the user to choose between a set of configurations.

    Return (config_name, cmake_generator)
    or none if user did not choose anything

    """
    known_configs = [
        "linux32",
        "linux64",
        "mac32",
        "mac64",
        "mingw32",
        "win32-vs2008",
        "win32-vs2010"
    ]
    config = qibuild.interact.ask_choice(known_configs, "please choose a configuration")
    if not config:
        return None

    if "vs2008" in config:
        cmake_generator = "Visual Studio 2008"
    elif "vs2010" in config:
        cmake_generator = "Visual Studio 2010"
    elif "mingw32" in config:
        # Check that mingw32-make.exe is in %PATH%:
        mingw32_make = qibuild.command.find_program("mingw32-make")
        qibuild.command.find_program
        if not mingw32_make:
            raise Exception("Could not find mingw32.exe in %PATH%\n"
                "Please check your environment variable settings, "
                "or choose an other configuration")
    else:
        cmake_generator = "Unix Makefiles"

    return (config, cmake_generator)

def run_wizard(toc):
    """Write a new configuration if the file passed as
    argument, asking the user a few questions

    """
    config = ask_config(toc)
    if not config:
        return

    (config_name, cmake_generator) = config

    toc.update_config("cmake.generator", cmake_generator, config=config_name)

    config_names = toc.configstore.get_known_configs()
    default_config = None
    if len(config_names) == 1:
        default_config = config_names[0]
    else:
        answer = qibuild.interact.ask_yes_no("Use %s as default config" % config_name)
        if answer:
            default_config = config_name

    if default_config:
        qibuild.configstore.update_config(toc.config_path, "general", "config", default_config)

