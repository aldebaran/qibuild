## Copyright (C) 2011 Aldebaran Robotics

"""Install a new toolchain

This makes it possible to use a toolchain with qibuild
First call:
    qitoolchain install NAME /path/to/toolchain/toolchain.cmake

Then you can use your toolchain with:
    qibuild -c NAME configure
    qibuild -c NAME build


You can edit the .qi/qibuild-NAME.cfg file if you wish.
"""

import logging
import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.qiworktree.work_tree_parser(parser)
    parser.add_argument("name",
        help="The name of the toolchain file")
    parser.add_argument("toolchain_file",
        help="Path to the toolchain file to use")
    parser.add_argument("--cross", action="store_true",
        help="This toolchain is a cross toolchain")
    parser.add_argument("--default", action="store_true",
        help="Use this toolchain by default")

def do(args):
    """Main entry point """
    tc_file = qibuild.sh.to_native_path(args.toolchain_file)
    tc_name = args.name


    tc_cfg = qitoolchain.get_tc_config_path()
    qitoolchain.set_tc_config(tc_name, "file", tc_file)

    if args.cross:
        qibuild.configstore.update_config(tc_name, "cross", "yes")

    if not args.default:
        mess  = "Not try using: \n"
        mess += "qibuild configure -c {tc_name} \n"
        mess += "qibuild make      -c {tc_name} \n"
        LOGGER.info(mess.format(tc_name=tc_name))
        return

    toc = None
    try:
        # Set the default toolchain for the crrent work_tree, if any:
        toc = qibuild.toc.toc_open(args.work_tree)
    except qibuild.toc.TocException, e:
        mess  = "Could not a find a worktree and --default is used\n"
        mess += "Please go to a valid worktree,\n"
        mess += "or specify a valid worktree with --workt-tree\n"
        mess += "and try again\n"
        raise Exception(mess)

    # We got a toc and args.default was set,
    # let's update current toc config:
    qibuild.configstore.update_config(toc.config_path, "general", "config", tc_name)

    LOGGER.info("Now using %s toolchain by default in worktree %s", tc_name, toc.work_tree)
