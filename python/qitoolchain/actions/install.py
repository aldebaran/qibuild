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
    qibuild.cmdparse.default_parser(parser)
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
    tc_file = qibuild.sh.to_native_path(args.toolchain_file)
    tc_name = args.name

    tc_cfg = qitoolchain.get_tc_config_path()
    qibuild.configstore.update_config(tc_cfg,
        "toolchain", tc_name, "file", tc_file)

    if args.cross:
        qibuild.configstore.update_config(tc_cfg,
            "toolchain", tc_name, "cross", "yes")

    cfg_path = qibuild.configstore.get_config_path(tc_name)

    if args.generator:
        # Fixme: open toc without passing build args...
        #qibuild.configstore.update_config(cfg_path,
            #"cmake.generator", args.generator)
        """
        toc.update_config("build", "cmake.generator", arg.generator, config=tc_name)
        """
        pass


    if not args.default:
        mess  = "Not try using: \n"
        mess += "qibuild configure -c {tc_name} \n"
        mess += "qibuild make      -c {tc_name} \n"
        LOGGER.info(mess.format(tc_name=tc_name))
        return

    #qibuild.configstore.update_config(cfg_path, "general", "config", tc_name)
    """
    qibuild.configstore.update_config(toc.config_path, "general", "config", tc_name)
    """
    LOGGER.info("Now using %s toolchain by default", tc_name)
