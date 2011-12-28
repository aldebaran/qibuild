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

"""Run the same command on each buildable project.

Use -- to separate qibuild arguments from the arguments of the command.
For instance
  qibuild --ignore-errors -- ls -l
"""

import logging
import qibuild


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("--ignore-errors", action="store_true", help="continue on error")

def do(args):
    """Main entry point"""
    qiwt = qibuild.worktree_open(args.work_tree)
    logger = logging.getLogger(__name__)
    for pname, ppath in qiwt.buildable_projects.iteritems():
        logger.info("Running `%s` for %s", " ".join(args.command), pname)
        try:
            qibuild.command.call(args.command, cwd=ppath)
        except qibuild.command.CommandFailedException, err:
            if args.ignore_errors:
                logger.error(str(err))
                continue
            else:
                raise

