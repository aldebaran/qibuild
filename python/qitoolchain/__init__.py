## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" qitoolchain: a package to handle set of precompiled
packages

"""

import qibuild

from qitoolchain.toolchain import Toolchain, Package
from qitoolchain.toolchain import get_tc_names, get_tc_config_path
from qitoolchain import remote
from qitoolchain import feed
from qitoolchain import version



def get_toolchain(args):
    """ Get a toolchain from the result of an argument parsing

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

    return Toolchain(tc_name)
