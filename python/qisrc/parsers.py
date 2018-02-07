# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Common parsers for qisrc actions """

import os

from collections import OrderedDict

import qisys.parsers
import qisys.worktree
import qisrc.worktree
import qisrc.git
import qibuild.deps
import qibuild.parsers
import qibuild.worktree


def worktree_parser(parser):
    qisys.parsers.worktree_parser(parser)


def groups_parser(parser):
    """Parsers settings for groups."""
    parser.add_argument("-g", "--group", dest="groups", action="append",
                        help="Specify a group of projects.")


def get_git_worktree(args):
    """ Get a git worktree to use

    """
    worktree = qisys.parsers.get_worktree(args)
    git_worktree = qisrc.worktree.GitWorkTree(worktree)
    return git_worktree


def get_git_projects(git_worktree, args,
                     default_all=False,
                     use_build_deps=False,
                     groups=None):
    """ Get a list of git projects to use """
    git_parser = GitProjectParser(git_worktree)
    groups = vars(args).get("groups")
    if groups:
        use_build_deps = False

    if use_build_deps:
        # To avoid getting all the projects when no project is given
        # and running from the subdir of a build project
        if not at_top_worktree(git_worktree):
            default_all = False
        build_worktree = qibuild.worktree.BuildWorkTree(git_worktree.worktree)
        build_parser = GitBuildProjectParser(git_worktree, build_worktree)
        return build_parser.parse_args(args, default_all=default_all)

    if groups:
        return git_worktree.get_git_projects(groups=groups)

    return git_parser.parse_args(args, default_all=default_all)


def get_one_git_project(git_worktree, args):
    parser = GitProjectParser(git_worktree)
    projects = parser.parse_args(args)
    if not len(projects) == 1:
        raise Exception("This action can only work with one project")
    return projects[0]


##
# Implementation details

def at_top_worktree(git_worktree):
    """ Return True if we are at the root of the worktree """
    return os.getcwd() == git_worktree.root


class GitProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a GitWorkTree """

    def __init__(self, git_worktree):
        super(GitProjectParser, self).__init__()
        self.git_worktree = git_worktree
        self.git_projects = git_worktree.git_projects
        self.wt_parser = qisys.parsers.WorkTreeProjectParser(git_worktree.worktree)

    def all_projects(self, args):
        return self.git_worktree.git_projects

    def parse_no_project(self, args):
        repo_root = qisrc.git.get_repo_root(os.getcwd())
        if not repo_root:
            raise qisrc.worktree.NotInAGitRepo()
        git_project = self.git_worktree.get_git_project(repo_root,
                                                        auto_add=True, raises=False)
        return [git_project]

    def parse_one_project(self, args, project_arg):
        # WorkTreeProjectParser.parse_one_project only returns
        # a list of one element or raises
        worktree_projects = self.wt_parser.parse_one_project(args, project_arg)
        worktree_project = worktree_projects[0]
        # closest git_project
        parent_git_project = qisys.parsers.find_parent_project(self.git_projects,
                                                               worktree_project.path)
        if parent_git_project:
            return [parent_git_project]


class GitBuildProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a GitWorkTree when
    --use-deps is used.

    """

    def __init__(self, git_worktree, build_worktree):
        super(GitBuildProjectParser, self).__init__()
        self.git_worktree = git_worktree
        self.build_worktree = build_worktree
        self.parser = GitProjectParser(git_worktree)
        self.build_parser = qibuild.parsers.BuildProjectParser(self.build_worktree)

    def all_projects(self, args):
        """ Implements AbstractProjectParser.all_projects """
        return self.git_worktree.git_projects

    def parse_one_project(self, args, project_arg):
        """ Implements AbstractProjectParser.parse_one_project """
        git_project = self.parser.parse_one_project(args, project_arg)[0]
        return [git_project]

    def parse_no_project(self, args):
        """ Implements AbstractProjectParser.parse_no_project """
        git_project = self.parser.parse_no_project(args)[0]
        return self.solve_deps(args, git_project)

    def solve_deps(self, args, git_project):
        """ Called when use_build_deps is True

        * find the current build project as qibuild would do
        * solve the dependencies
        * find the git projects matching the dependencies

        """
        build_project = None
        try:
            build_project = self.build_parser.parse_no_project(args)[-1]
        except qibuild.parsers.CouldNotGuessProjectName:
            pass
        if not build_project:
            return [git_project]
        git_projects = list()  # Order matters
        deps_solver = qibuild.deps.DepsSolver(self.build_worktree)
        dep_types = qibuild.parsers.get_dep_types(args)
        deps_solver.dep_types = dep_types
        build_projects = deps_solver.get_dep_projects([build_project], dep_types)
        for build_project in build_projects:
            git_project = qisys.parsers.find_parent_project(self.git_worktree.git_projects,
                                                            build_project.path)
            git_projects.append(git_project)
        # Idiom to sort an iterable preserving order
        return list(OrderedDict.fromkeys(git_projects))
