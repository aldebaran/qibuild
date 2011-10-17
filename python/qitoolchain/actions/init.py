## Copyright (C) 2011 Aldebaran Robotics

""" Configure a worktree to use a toolchain.

Toolchain packages and known configurations will be fetched from an URL.

"""

import os
import logging

import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)

KNOWN_CONFIGS = [
    'linux32',
    'mac32',
    'win32-vs2008',
    'win32-vs2010',
    'geode',
    'atom']


def configure_parser(parser):
    """Configure parse for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("--tc-file", metavar="TOOLCHAIN_FILE",
        help="Path to the toolchain file.\n"
             "Mandatory if no name was given")
    parser.add_argument("--name",
        help="Name of the toolchain to create.\n"
             "Mandatory if no toolchain file was given")
    parser.add_argument("--cmake-generator",
        help="Name of the CMake generator to use.\n"
             "Guessed from the toolchain name")
    parser.add_argument("--default",
        help="Use this toolchain by default in this worktree",
        action="store_true")

def guess_tc_name(tc_file):
    """ Guess the name of the toolchain from the toolchain file

    """
    root_dir = os.path.dirname(tc_file)
    basename = os.path.basename(root_dir)
    for config in KNOWN_CONFIGS:
        if config in basename:
            return config
    mess  = "Could not guess config name from toolchain file %s\n" % tc_file
    mess += "Used base directory: %s\n" % basename
    mess += "But this directory does not contain any know config.\n"
    mess += "Known configs are: %s\n" % ", ".join(KNOWN_CONFIGS)

def guess_generator(tc_name):
    """ Guess the CMake generator from the config name

    """
    if tc_name == "win32-vs2010":
        return 'Visual Studio 10'
    elif tc_name == "win32-vs2008":
        return 'Visual Studio 9 2008'
    return 'Unix Makefiles'

def do(args):
    """Main entry point

    """
    tc_file = args.tc_file
    tc_file = qibuild.sh.to_native_path(tc_file)
    tc_name = args.name
    if not tc_name and not tc_file:
        raise Exception("Please use at least --tc-file or --name")

    if not tc_name:
        tc_name = guess_tc_name(tc_file)

    cmake_generator = args.cmake_generator

    if not cmake_generator:
        cmake_generator = guess_generator(tc_name)

    qitoolchain.set_tc_config(tc_name, "file", tc_file)

    toc = qibuild.toc.toc_open(args.work_tree)
    toc.update_config('cmake.generator', cmake_generator, config=tc_name)


    if args.default:
        toc.update_config("config", tc_name)
        LOGGER.info("Now using toolchain %s by default", tc_name)

    else:
        mess = """Now try using:
    qibuild configure -c {tc_name}
    qibuild make      -c ${tc_name}
"""
        mess = mess.format(tc_name=tc_name)
        LOGGER.info(mess)
