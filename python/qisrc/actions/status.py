## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the state of all git repositories and exit
"""

import os
import sys
import qibuild.log

import qibuild
import qisrc

LOGGER = qibuild.log.get_logger("qisrc.status")

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("--untracked-files", "-u",
        dest="untracked_files",
        action="store_true",
        help="display untracked files")
    parser.add_argument("--show-branch", "-b",
        dest="show_branch",
        action="store_true",
        help="display branch and tracking branch for each repository")

def _max_len(wt, projects):
    """ Helper function to display status """
    max_len = 0
    for p in projects:
        shortpath = os.path.relpath(p.src, wt)
        if len(shortpath) > max_len:
            max_len = len(shortpath)
    return max_len

def _add_pad(max_len, k, v):
    pad = " " * (max_len - len(k))
    return "%s%s%s" % (str(k), pad, str(v))

def _pad(szold, sznew):
    if sznew > szold:
        return ""
    return " " * (szold - sznew)

def stat_tracking_remote(git, branch, tracking):
    behind = 0
    ahead = 0
    (ret, out) = git.call("rev-list", "--left-right", "%s..%s" % (tracking, branch), raises=False)
    if ret == 0:
        ahead = len(out.split())
    (ret, out) = git.call("rev-list", "--left-right", "%s..%s" % (branch, tracking), raises=False)
    if ret == 0:
        behind = len(out.split())
    return (ahead, behind)

def do(args):
    """ Main method """
    qiwt = qisrc.open_worktree(args.worktree)
    gitrepo = list()
    dirty = list()
    incorrect = list()

    git_projects = qiwt.git_projects
    manifests = qiwt.get_manifest_projects()
    git_projects = list(set(git_projects) - set(manifests))

    sz = len(git_projects)
    i = 1
    oldsz = 0
    incorrect_projs = list()
    for git_project in git_projects:
        git = qisrc.git.open(git_project.path)
        if sys.stdout.isatty():
            src = git_project.src
            to_write = "checking (%d/%d)" % (i, sz)
            to_write += src
            to_write += _pad(oldsz, len(src))
            sys.stdout.write(to_write + "\r")
            sys.stdout.flush()
            oldsz = len(src)
            if i == sz:
                print "checking (%d/%d): done" % (i, sz), _pad(oldsz, 2)
        i = i + 1
        if git.is_valid():
            clean = git.is_clean(untracked=args.untracked_files)

            #clean worktree, but is the current branch sync with the remote one?
            if clean:
                branch = git.get_current_branch()
                if branch != git_project.branch:
                    incorrect_projs.append((git_project.src, branch, git_project.branch))
                    incorrect.append(git_project)
                tracking = git.get_tracking_branch()
                (ahead, behind) = stat_tracking_remote(git, branch, tracking)
                if ahead != 0 or behind != 0:
                    clean = False

            if args.show_branch or not clean:
                gitrepo.append(git_project)
            if not clean:
                dirty.append(git_project)

    LOGGER.info("Dirty projects: %d/%d", len(dirty), len(qiwt.git_projects))

    max_len = _max_len(qiwt.root, gitrepo)
    for git_project in gitrepo:
        git = qisrc.git.open(git_project.path)
        shortpath = os.path.relpath(git_project.path, qiwt.root)
        if git.is_valid():
            branch = git.get_current_branch()
            tracking = git.get_tracking_branch()
            line = _add_pad(max_len, shortpath, " : %s tracking %s" %
                (branch, tracking))
            (ahead, behind) = stat_tracking_remote(git, branch, tracking)
            LOGGER.info(line)
            if ahead:
                print(" ## Your branch is %d commits ahead" % ahead)
            if behind:
                print(" ## Your branch is %d commits behind" % behind)

        if not git.is_clean(untracked=args.untracked_files):
            if args.untracked_files:
                (status_, out) = git.call("status", "-s", raises=False)
            else:
                (status_, out) = git.call("status", "-suno", raises=False)
            nlines = [ x[:3] + shortpath + "/" + x[3:] for x in out.splitlines() if len(x.strip()) > 0 ]
            print "\n".join(nlines)

    max_len = _max_len(qiwt.root, incorrect)
    max_len = max([max_len, len("Project")])
    if incorrect_projs:
        max_branch_len = max([len(x[1]) for x in incorrect_projs])
        max_branch_len = max([max_branch_len, len("Current")])
        print
        print " ## Warning: some projects are not on the expected branch"
        LOGGER.info("Project".ljust(max_len + 3) + "Current".ljust(max_branch_len + 3) + "Manifest")
        for (project, local_branch, manifest_branch) in incorrect_projs:
            LOGGER.info(project.ljust(max_len + 3) + local_branch.ljust(max_branch_len + 3) + manifest_branch)

    if not args.untracked_files:
        print
        print("Tips: use -u to show untracked files")

