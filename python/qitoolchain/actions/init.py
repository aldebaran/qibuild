## Copyright (C) 2011 Aldebaran Robotics

""" Configure a worktree to use a toolchain.

Toolchain packages and known configurations will be fetched from an URL.

"""

import sys
import logging

import qibuild

LOGGER = logging.getLogger(__name__)



def configure_parser(parser):
    """Configure parse for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("-c", "--config",
        choices=KNOWN_CONFIGS)
    parser.add_argument("toolchain_url")




def do(args):
    """Main entry point

    """
    toc = qibuild.toc.toc_open(args.work_tree)

    tc_url = args.toolchain_url
    config = args.config
    if not config:
        config = qibuild.interact.ask_choice(KNOWN_CONFIGS,
            "Please choose a configuration")
    feed_url = "ftp://ananas/qi/feeds/%s.cfg" % config
    qibuild.run_action("qidev.actions.update_toolchain",
            [config, feed_url])

    if "vs2008" in config:
        cmake_generator = "Visual Studio 9 2008"
    elif "vs2010" in config:
        cmake_generator = "Visual Studio 10"
    else:
        cmake_generator = "Unix Makefiles"


    toc_cfg = toc.config_path
    qibuild.configstore.update_config(toc_cfg, "general", "config", config)

    toc.update_config('cmake.generator', cmake_generator, config)
