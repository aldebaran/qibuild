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

""" List all git repositories and exit
"""

import os
import sys
import logging

import qibuild
import qisrc

LOGGER = logging.getLogger("qisrc.status")

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("--untracked-files", "-u", dest="untracked_files", action="store_true", help="display untracked files")
    parser.add_argument("--show-branch", "-b", dest="show_branch", action="store_true", help="display branch and tracking branch for each repository")

def _max_len(wt, names):
    """ Dump an argparser namespace to log """
    output = ""
    max_len = 0
    for k in names:
        shortpath = os.path.relpath(k, wt)
        if len(shortpath) > max_len:
            max_len = len(shortpath)
    return max_len

def _add_pad(max_len, k, v):
    pad = "".join([ " " for x in range(max_len - len(k)) ])
    return "%s%s%s" % (str(k), pad, str(v))

def _pad(szold, sznew):
    if sznew > szold:
        return ""
    return "".join([ " " for x in range(szold - sznew)])


def do(args):
    """ Main method """
    qiwt = qibuild.worktree_open(args.work_tree)
    gitrepo = list()
    dirty = list()
    sz = len(qiwt.git_projects.values())
    i = 1
    oldsz = 0
    for git_project in qiwt.git_projects.values():

        git = qisrc.git.open(git_project)
        pad = ""
        if sys.stdout.isatty():
            name = os.path.split(git_project)
            name = git_project if len(name) <= 0 else name[-1]
            print "checking (%d/%d): " % (i, sz), name, _pad(oldsz, len(name)), "\r",
            oldsz = len(name)
            if i == sz:
                print "checking (%d/%d): done" % (i, sz), _pad(oldsz, 2)
        i = i + 1
        if git.is_valid():
            clean = git.is_clean(untracked=args.untracked_files)
            if args.show_branch or not clean:
                gitrepo.append(git_project)
            if not clean:
                dirty.append(git_project)

    LOGGER.info("Dirty projects: %d/%d", len(dirty), len(qiwt.git_projects))

    max_len = _max_len(qiwt.work_tree, gitrepo)
    for git_project in gitrepo:
        git = qisrc.git.open(git_project)
        shortpath = os.path.relpath(git_project, qiwt.work_tree)
        if git.is_valid():
            line = _add_pad(max_len, shortpath, " : %s tracking %s" % (git.get_current_branch(), git.get_tracking_branch()))
            LOGGER.info(line)
        if not git.is_clean(untracked=args.untracked_files):
            if args.untracked_files:
                lines = git.cmd.call_output("status", "-s")
            else:
                lines = git.cmd.call_output("status", "-suno")
            nlines = [ x[:3] + shortpath + "/" + x[3:] for x in lines if len(x.strip()) > 0 ]
            print "\n".join(nlines)


    if not args.untracked_files:
        print
        print("Tips: use -u to show untracked files")

