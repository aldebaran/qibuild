## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" qitoolchain: a package to handle set of precompiled
packages

"""

import qisys.error

from qitoolchain.toolchain import Toolchain
from qitoolchain.toolchain import get_tc_names

def get_toolchain(tc_name):
    """ Get an existing tolchain using its name """
    tc_names = get_tc_names()
    if not tc_name in tc_names:
        mess  = "No such toolchain: %s\n" % tc_name
        mess += "Known toolchains are:\n"
        for name in tc_names:
            mess +=  "  * " + name + "\n"
        raise qisys.error.Error(mess)
    return Toolchain(tc_name)
