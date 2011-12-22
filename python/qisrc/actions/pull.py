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

""" Run git pull on every git projects of a worktree

"""

import os
import logging
import qibuild
import qisrc

from qibuild.dependencies_solver import DependenciesSolver

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--rebase", action="store_true", dest="rebase",
        help="Use git pull --rebase")
    parser.set_defaults(rebase=False)


def uniq(lst):
    checked = []
    for e in lst:
        if e not in checked:
            checked.append(e)
    return checked

#for each qibuild project, find the associated git_project if any
def toc_dep_to_git_proj(names, git_projects):
    ret = list()
    for n in names:
        cur = ""
        for g in git_projects:
            if n.startswith(g) and len(g) > len(cur):
                cur = g
        if cur:
            ret.append(cur)
    return uniq(ret)

#for each git project find all toc associated projects
def git_dep_to_toc_dep(names, toc_projects):
    ret = list()
    for g in names:
        for t in toc_projects:
            if t.directory.startswith(g):
                ret.append(t.name)
    return ret

def _search_git_directory(working_directory):
    """ find the manifest associated to the working_directory, return None if not found """
    cwd     = os.path.normpath(os.path.abspath(working_directory))
    dirname = None

    #for each cwd parent folders, try to see if it match src
    while dirname or cwd:
        if os.path.isdir(os.path.join(cwd, ".git")):
            return cwd
        (new_cwd, dirname) = os.path.split(cwd)
        if new_cwd == cwd:
            break
        cwd = new_cwd
    return None

def resolv_git_deps(toc, qiwt, args):

    project_names = None

    #all
    if args.all:
        LOGGER.debug("All projects have been selected")
        project_names = qiwt.git_projects.values()
        return project_names

    #no specified projects, search on cwd, fallback on all
    if not len(args.projects):
        pn = _search_git_directory(os.getcwd())
        if pn:
            LOGGER.debug("Selecting project from cwd.")
            project_names = [pn]
        else:
            LOGGER.debug("Selecting project all projects (none specified, and no in cwd).")
            project_names = qiwt.git_projects.values()
            return project_names
    else:
        project_names = list()
        for p in args.projects:
            if not qiwt.git_projects.get(p):
                raise Exception("Cant find %s\n" % (p))
            project_names.append(qiwt.git_projects[p])

    #single => no deps, returns
    if args.single:
        LOGGER.debug("Single project selected")
        return project_names

    # # Magic happen here #
    #convert git-project-list to a toc-project-list
    #resolv deps
    #convert the toc-project-list to git-project-list again
    #merge new deps into current list of git projects
    toc_projects = git_dep_to_toc_dep(project_names, toc.projects)

    dep_solver = DependenciesSolver(projects=toc.projects, packages=toc.packages)
    (all_toc_projects, _, _) = dep_solver.solve(toc_projects, runtime=False)
    toc_project_names = [ toc.get_project(x).directory for x in all_toc_projects ]
    new_toc_deps = toc_dep_to_git_proj(toc_project_names, qiwt.git_projects.values())
    new_toc_deps.extend(project_names)
    return uniq(new_toc_deps)



def do(args):
    """Main entry point"""
    fail = list()
    qiwt = qibuild.worktree_open(args.work_tree)
    toc  = qibuild.toc_open(args.work_tree, args)

    toc_cfg = toc.config_path
    toc_configstore = qibuild.configstore.ConfigStore()
    toc_configstore.read(toc_cfg)
    manifest_url = toc_configstore.get("manifest.url")
    if manifest_url:
        try:
            qibuild.run_action("qisrc.actions.fetch",
                args=[manifest_url],
                forward_args=args)
        except Exception, e:
            mess  = "Could not run qisrc fetch\n"
            mess += "Error was: %s\n" % e
            LOGGER.warning(mess)

    project_names = resolv_git_deps(toc, qiwt, args)

    for git_project in project_names:
        git = qisrc.git.open(git_project)
        LOGGER.info("Pull %s", git_project)
        if args.rebase:
            out = git.cmd.call_output("pull", "--rebase", rawout=True)
        else:
            out = git.cmd.call_output("pull", rawout=True)
        if out[0] == 0:
            print out[1][1],
            print out[1][0],
        else:
            LOGGER.error("failed")
            fail.append((git_project, out))

    if len(fail) > 0:
        print ""
        LOGGER.info("=====================")
        LOGGER.info("Projects that failed:")
        print "\n".join(x[0] for x in fail)
        LOGGER.info("=====================")
        print ""
        LOGGER.info("details:")

    for f in fail:
        LOGGER.error(f[0])
        print f[1][1][0],
        print f[1][1][1],
