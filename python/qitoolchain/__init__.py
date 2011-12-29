## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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
            toc = qibuild.toc.toc_open(args.work_tree, args)
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
