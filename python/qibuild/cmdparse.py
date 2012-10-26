## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" Parsing of qisys.command line arguments

"""

import os

from qisys import ui
import qisys
import qibuild
import qibuild.toc
from qibuild.dependencies_solver import topological_sort

def get_deps(toc, projects, single=False, runtime=False, build_deps=False):
    """ Get a list (packages, projects) from a toc object,
    some projects and some flags

    """
    orig_list = [x.name for x in projects]
    if single:
        return (list(), projects)
    to_sort = dict()
    if build_deps:
        for project in toc.projects:
            to_sort[project.name] = project.depends
    elif runtime:
        for project in toc.projects:
            to_sort[project.name] = project.rdepends
    else:
        for project in toc.projects:
            to_sort[project.name] = project.rdepends.union(project.depends)

    names = topological_sort(to_sort, [x.name for x in projects])

    package_names = list()
    if toc.toolchain:
        package_names = [x.name for x in toc.toolchain.packages]
    project_names = [x.name for x in toc.projects]

    r_projects = list()
    r_packages = list()
    for name in names:
        if name in orig_list:
            r_projects.append(toc.get_project(name))
        elif name in package_names:
            r_packages.append(toc.get_package(name))
        elif name in project_names:
            r_projects.append(toc.get_project(name))
    return (r_packages, r_projects)

def parse_project_arg(toc, arg):
    """ Parse one project arg.
    arg can be:
        * a absolute path to a qibuild project
        * the path to a qibuild project relative to the worktree root
        * a project name
    """
    as_path = qisys.sh.to_native_path(arg)
    if os.path.exists(as_path):
        p_name = qibuild.project.project_from_dir(toc, directory=as_path, raises=False)
        if p_name:
            return toc.get_project(p_name)
    else:
        # Try a relative path to to root:
        as_path = os.path.join(toc.worktree.root, arg)
        if os.path.exists(as_path):
            p_name = qibuild.project.project_from_dir(toc, directory=as_path, raises=False)
            if p_name:
                return toc.get_project(p_name)

    # Assume it's a name:
    return toc.get_project(arg, raises=True)


def project_from_args(toc, args):
    """ Parse one or zero project name on the command line.

    If not name given guess it from the working directory
    Else:
        * try to find a qibuild project matching by path
        * try to find a qibuild project matching by name
        * raise if both fail

    """
    if not args.project:
        project_arg = qibuild.project.project_from_dir(toc)
    else:
        project_arg = args.project
    return parse_project_arg(toc, project_arg)


def deps_from_args(toc, args):
    """ Return a tuple (package, projects) of
    dependency to use.

    * --worktree not given: guess the worktree from cwd
    * project names list empty:
        * if at the root of the worktree or --all: return every project
        * if in a subdirectory of a project: the matching project
        * raise
    * for each project in the list:
        * if --build-deps: sorted list of the given project list and
          only their build deps
        * if --runtime: sorted list of the given projct list and
          their runtime deps
        * if --single: only the given list
        * default: sorted list of the given project list and their
          deps (both runtime and buildtime)

    """
    wt_root = toc.worktree.root
    if args.all:
        return(toc.packages, toc.projects)
    if args.worktree and not args.projects:
        mess  = "Specifying a project name is mandatory when using --worktree"
        raise Exception(mess)
    if args.projects:
        project_args = args.projects
    else:
        if os.getcwd() == wt_root:
            no_project_args_on_root(toc.worktree)
        project_args = [qibuild.project.project_from_dir(toc)]

    # Now project_names is the list of explicitely asked projects
    # or a list of one element containing the guessed project name
    # from cwd
    projects = [parse_project_arg(toc, x) for x in project_args]
    toc.active_projects = [x.name for x in projects]
    deps = get_deps(toc, projects, single=args.single,
                    runtime=args.runtime, build_deps=args.build_deps)
    return deps


def no_project_args_on_root(worktree):
    """ Called when user ran a qisys.command at the top
    of a worktree.


    """
    wt_root = worktree.root
    qiproj_xml = os.path.join(wt_root, "qiproject.xml")
    if os.path.exists(qiproj_xml):
        mess  = """ Found a qiproject.xml at the root of the worktree
(in {qiproj_xml})

This is not recommended. You should create your worktree at
the parent directory instead

Please remove {dot_qi} and run:

    cd {parent}
    qibuild init

to do so
"""
        parent = os.path.join(wt_root, "..")
        parent = os.path.abspath(parent)
        mess = mess.format(qiproj_xml=qiproj_xml, wt_root=wt_root,
                           parent=parent,
                           dot_qi=os.path.join(wt_root, ".qi"))

        ui.warning(mess, end="")
    else:
        mess = """No project specified
Please specify the name or the path of a project
or go to the subdirectory of a project
Tip: use `qibuild list' to get the list of known projects"""
        raise Exception(mess)
