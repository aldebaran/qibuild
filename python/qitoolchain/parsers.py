# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import qisys.worktree
import qibuild.parsers

import qibuild.config
import qitoolchain


def toolchain_parser(parser):
    """ Parser for every action that requires a toolchain """
    parser.add_argument("-c", "--config", dest="config",
                        help="Name of a config to use. The config should be associated to a toolchain")
    parser.add_argument("-t", "--toolchain", dest="toolchain_name",
                        help="Name of the toolchain to use")


def get_toolchain(args):
    """ Get the toolchain to use.
    If we are inside a build worktree, return the default
    toolchain is this worktree

    """
    if args.toolchain_name:
        return qitoolchain.get_toolchain(args.toolchain_name)

    config = args.config
    if not config:
        try:
            build_worktree = qibuild.parsers.get_build_worktree(args)
            active_build_config = build_worktree.build_config.active_build_config
            if active_build_config:
                config = active_build_config.toolchain
            else:
                config = None
        except qisys.worktree.NotInWorkTree:
            config = None

    if not config:
        mess = "Could not find which config to use.\n"
        mess += "(not in a work tree or no default config in "
        mess += "current worktree configuration)\n"
        mess += "Please specify a configuration with -c, --config \n"
        mess += "or a toolchain name with -t, --toolchain"
        raise Exception(mess)

    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    build_config = qibuild_cfg.configs.get(config)
    if not build_config:
        raise Exception("No such config: %s" % config)
    tc_name = build_config.toolchain
    if not tc_name:
        raise Exception("config %s has no toolchain" % config)
    return qitoolchain.get_toolchain(tc_name)
