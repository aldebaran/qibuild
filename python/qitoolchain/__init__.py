## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" qitoolchain: a package to handle set of precompiled
packages

"""

import qibuild

from qitoolchain.toolchain import Toolchain, Package
from qitoolchain.toolchain import get_tc_names, get_tc_config_path



def toolchain_name_from_args(args):
    """ Get a toolchain from the result of an argument parsing
    (using a worktree parser)

    """
    tc_name = args.config
    if not tc_name:
        active_config = None
        try:
            toc = qibuild.toc.toc_open(args.worktree, args)
            active_config = toc.active_config
        except qibuild.toc.TocException:
            pass
        if not active_config:
            mess  = "Could not find which config to use.\n"
            mess += "(not in a work tree or no default config in "
            mess += "current worktree configuration)\n"
            mess += "Please specify a configuration with -c \n"
            raise Exception(mess)
        tc_name = active_config
    return tc_name


def get_toolchain(tc_name):
    """ Get an existing tolchain using its """
    tc_names = get_tc_names()
    if not tc_name in tc_names:
        mess  = "No such toolchain: %s\n" % tc_name
        mess += "Known toolchains are:\n"
        for name in tc_names:
            mess +=  "  * " + name + "\n"
        raise Exception(mess)
    return Toolchain(tc_name)
