## Copyright (C) 2011 Aldebaran Robotics

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
    parser.add_argument("--continue", action="store_true", dest="continue_on_error", help="continue on error")
    parser.add_argument("--stop-on-error", action="store_false", dest="continue_on_error", help="continue on error")
    parser.add_argument("--rebase", action="store_true", dest="rebase", help="rebase")
    parser.set_defaults(continue_on_error=True)


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

    project_names = resolv_git_deps(toc, qiwt, args)

    for git_project in project_names:
        git = qisrc.git.open(git_project)
        LOGGER.info("Pull %s", git_project)
        if args.rebase:
            out = git.cmd.call_output("pull", "--rebase", rawout=True)
        else:
            out = git.cmd.call_output("pull", rawout=True)
        out = git.cmd.call_output("pull", rawout=True)
        if out[0] == 0:
            print out[1][0],
            print out[1][1],
        else:
            fail.append((git_project, out))
            if not args.continue_on_error:
                raise Exception("\n%s%s" % (out[1][0], out[1][1]))

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
