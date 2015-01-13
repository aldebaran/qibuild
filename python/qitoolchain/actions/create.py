## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Configure a worktree to use a toolchain.

Toolchain packages and known configurations will be fetched from an URL.

"""

from qisys import ui
import qisys.parsers
import qibuild.parsers
import qitoolchain


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name", metavar="NAME",
        help="Name of the toolchain")
    parser.add_argument("feed", metavar="TOOLCHAIN_FEED",
        help="Optional: path to the toolchain configuration file.\n"
             "If not given, the toolchain will be empty.\n"
             "May be a local file or an url",
        nargs="?")
    parser.add_argument("--default",
        help="Use this toolchain by default in this worktree",
        action="store_true")

def do(args):
    """Main entry point

    """
    feed = args.feed
    tc_name = args.name

    # Validate the name: must be a valid filename:
    bad_chars = r'<>:"/\|?*'
    for bad_char in bad_chars:
        if bad_char in tc_name:
            mess  = "Invalid toolchain name: '%s'\n" % tc_name
            mess += "A valid toolchain name should not contain any "
            mess += "of the following chars:\n"
            mess += " ".join(bad_chars)
            raise Exception(mess)

    if tc_name == "system":
        raise Exception("'system' is a reserved name")

    build_worktree = None

    if args.default:
        try:
            build_worktree = qibuild.parsers.get_build_worktree(args)
        except qisys.worktree.NotInWorkTree:
            mess = "You need to be in a worktree to use --default"
            raise Exception(mess)

    if tc_name in qitoolchain.get_tc_names():
        toolchain = qitoolchain.Toolchain(tc_name)
        if feed and toolchain.feed_url != feed:
            ui.warning(tc_name, "already exists but points to a different feed,",
                   "removing previous toolchain and creating a new one")
            toolchain.remove()
        else:
            ui.info(tc_name, "already exists,",
                   "updating without removing")

    toolchain = qitoolchain.Toolchain(tc_name)
    if feed:
        toolchain.update(feed)

    if args.default:
        build_worktree.set_default_config(tc_name)
        ui.info("Now using toolchain", ui.blue, tc_name, ui.reset, "by default")
    else:
        ui.info(ui.green, "Now try using", "\n"
                "  qibuild configure -c", ui.blue, tc_name, ui.green, "\n"
                "  qibuild make -c",      ui.blue, tc_name)
    return toolchain
