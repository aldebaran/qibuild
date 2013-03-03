## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Common parsers for qisrc actions """

import os

import qisys.parsers
import qisys.worktree
import qisrc.worktree
import qisrc.git
import qibuild.parsers
import qibuild.worktree

def worktree_parser(parser):
    qisys.parsers.worktree_parser(parser)

def groups_parser(parser):
    """Parsers settings for groups."""
    parser.add_argument("-g", "--group", dest="groups", action="append",
                        help="Specify a group of projects.")

def get_git_worktree(args, sync_first=True):
    """ Get a git worktree to use

    """
    worktree = qisys.parsers.get_worktree(args)
    git_worktree = qisrc.worktree.GitWorkTree(worktree, sync_first=sync_first)
    return git_worktree


def get_git_projects(git_worktree, args):
    """ Get a list of git projects to use """
    if args.build_deps:
        build_worktree = qibuild.worktree.BuildWorkTree(git_worktree.worktree)
        parser = GitBuildProjectParser(git_worktree, build_worktree)
    else:
        parser = GitProjectParser(git_worktree)
    return parser.parse_args(args)

##
# Implementation details

class GitProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a GitWorkTree """
    def __init__(self, git_worktree):
        self.git_worktree = git_worktree
        self.git_projects = git_worktree.git_projects
        self.wt_parser = qisys.parsers.WorkTreeProjectParser(git_worktree.worktree)


    def all_projects(self):
        return self.git_worktree.git_projects

    def parse_no_args(self):
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
    def __init__(self, git_worktree, build_worktree):
        self.build_worktree = build_worktree
        self.build_parser = qibuild.parsers.BuildProjectParser(build_worktree)
        self.build_projects = self.build_worktree.build_projects
        self.git_worktree = git_worktree
        self.git_parser = GitProjectParser(git_worktree)
        self.git_projects = self.git_worktree.git_projects

    def all_projects(self):
        return self.git_worktree.git_projects

    def parse_one_project(self, args, project_arg):
        """ Parse one project:

        Find all the build deps, then find every git project that contains
        the build depencencies

        """
        build_projects =  self.build_parser.parse_one_project(args, project_arg)
        git_projects = list()
        for build_project in build_projects:
            git_project = qisys.parsers.find_parent_project(self.git_projects,
                                                            build_project.path)
            git_projects.append(git_project)
        return git_projects

    def parse_no_args(self):
        # solve deps
        pass
