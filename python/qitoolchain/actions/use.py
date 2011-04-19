## Copyright (C) 2011 Aldebaran Robotics

"""Tell qibuild what toolchain to use from
now on

"""

import qitools
import qibuild
import qitoolchain

def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)
    parser.add_argument("toolchain_name",
        help="name of the toolchain to use")

def do(args):
    """Main entry point"""
    name = args.toolchain_name
    qiwt = qitools.qiworktree_open(args.work_tree, use_env=True)
    config = qitools.configstore.ConfigStore()
    config.read(qitoolchain.get_tc_config_path())
    from_conf = config.get("toolchain", name)
    if from_conf is None:
        raise Exception("Could not find {name} in known toolchains.\n"
            "Try to run qitoolchain create {name}".format(name=name))
    tc = qitoolchain.Toolchain(name)
    config_path = qiwt.user_config_path
    qitools.configstore.update_config(config_path,
        "general", "build", "toolchain_file", tc.toolchain_file)

