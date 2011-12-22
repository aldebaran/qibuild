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

"""Display the status of each project
"""

import os
import glob
import time
import datetime
import logging
import qibuild

LOGGER = logging.getLogger(__name__)

def usage():
    "Specific usage"
    return """status [--all, -a] [projects...]"""

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)

def list_build_dir(path):
    """ list all buildable directory """
    bdirs = glob.glob(os.path.join(path, "build-*"))
    max_len = 0
    for bdir in bdirs:
        if len(bdir) > max_len:
            max_len = len(bdir)

    for bdir in bdirs:
        if os.path.isdir(bdir):
            ctim = time.time()
            ftim = os.path.getmtime(bdir)
            delta = ctim - ftim
            ddelta = datetime.timedelta(seconds = delta)
            todisplay = ""
            if ddelta.days > 0:
                todisplay = "%d days, %d hours" % (ddelta.days, ddelta.seconds / 3600)
            elif ddelta.seconds > 3600:
                todisplay = "%d hours" % (ddelta.seconds / 3600)
            else:
                todisplay = "%d minutes" % (ddelta.seconds / 60)
            pad = " " * (max_len - len(bdir))
            print " %s%s: (%s)" % (os.path.basename(bdir), pad, todisplay)

def do(args):
    """Main entry point"""
    qiwt = qibuild.worktree_open(args.work_tree)
    max_len = 0
    for pname, ppath in qiwt.buildable_projects.iteritems():
        if len(pname) > max_len:
            max_len = len(pname)

    for pname, ppath in qiwt.buildable_projects.iteritems():
        LOGGER.info("%s", os.path.relpath(ppath, qiwt.work_tree))
        list_build_dir(ppath)
