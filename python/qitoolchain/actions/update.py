## Copyright (C) 2011 Aldebaran Robotics

""" Update a toolchain
    This will try to update every package already found in the toolchain """

import qitools
import qitoolchain

def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)
    parser.add_argument("toolchain_name", nargs='?', metavar="TOOLCHAIN NAME",
        action="store", help="the toolchain name")
    parser.add_argument("--all", action="store_true", help="get all the projects known by the feed")
    parser.add_argument("toolchain_feed", nargs='?', metavar="FEED URL", action="store",
        help="an url to a toolchain feed. If not given, the previous feed will be used. "
             "Warning ! No backup is made if you change the toolchain feed")


def do(args):
    """Main method """
    toolchain_name = None
    if args.toolchain_name:
        toolchain_name = args.toolchain_name
    else:
        tc_from_conf = None
        try:
            qiwt = qitools.qiworktree_open(args.work_tree, use_env=True)
            tc_from_conf = qiwt.configstore.get("general", "build", "toolchain")
        except qitools.qiworktree.WorkTreeException:
            pass
        if not tc_from_conf:
            mess  = "Could not find default toolchain name in configuration.\n"
            mess += "Try specifying a toolchain name on the command line"
            raise Exception(mess)
        toolchain_name = tc_from_conf

    toolchain_feed = args.toolchain_feed
    toolchain = qitoolchain.Toolchain(toolchain_name)
    toolchain.update(toolchain_feed, all=args.all)

