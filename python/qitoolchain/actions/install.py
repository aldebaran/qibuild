## Copyright (C) 2011 Aldebaran Robotics

"""Install a new toolchain

This makes it possible to use a toolchain with qibuild
First call:
    qitoolchain install NAME /path/to/toolchain/toolchain.cmake

Then you can use your toolchain with:
    qibuild -c NAME configure
    qibuild -c NAME build


You can edit the .qi/build-NAME.cfg file if you wish.
"""

import os
import logging
import qitools
import qitoolchain

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)
    parser.add_argument("name",
        help="The name of the toolchain file")
    parser.add_argument("toolchain_file",
        help="Path to the toolchain file to use")
    parser.add_argument("--cross", action="store_true",
        help="This toolchain is a cross toolchain")
    parser.add_argument("--generator",
        help="Force CMake generator when using this toolchain")
    parser.add_argument("--default", action="store_true",
        help="Use this toolchain by default")


def do(args):
    """Main entry point """
    tc_file = qitools.sh.to_native_path(args.toolchain_file)
    tc_name = args.name

    tc_cfg = qitoolchain.get_tc_config_path()
    qitools.configstore.update_config(tc_cfg,
        "toolchain", tc_name, "file", tc_file)

    if args.cross:
        qitools.configstore.update_config(tc_cfg,
            "toolchain", tc_name, "cross", "yes")

    qiwt = qitools.qiworktree_open(args.work_tree, use_env=True)
    work_tree = qiwt.work_tree
    cfg_path = os.path.join(work_tree, ".qi", "build-%s.cfg" % tc_name)
    qitools.configstore.update_config(cfg_path,
        "general", "build", "toolchain", tc_name)

    if args.generator:
        qitools.configstore.update_config(cfg_path,
            "general", "build", "cmake_generator", args.generator)

    if not args.default:
        LOGGER.info("Now try using `qibuild -c %s'", tc_name)
        return

    cfg_path = qiwt.user_config_path
    qitools.configstore.update_config(cfg_path,
        "general", "build", "config", tc_name)
    LOGGER.info("Now using %s toolchain by default", tc_name)
