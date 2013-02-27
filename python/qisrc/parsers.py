## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Common parsers for qisrc actions """

import os

import qisys.parsers
import qisys.worktree
import qisrc.worktree
import qisrc.git

def worktree_parser(parser):
    qisys.parsers.worktree_parser(parser)

def groups_parser(parser):
    """Parsers settings for groups."""
    parser.add_argument("-g", "--group", dest="groups", action="append",
                        help="Specify a group of projects.")

def get_git_worktree(args):
    """ Get a git worktree to use """
    worktree = qisys.parsers.get_worktree(args)
    git_worktree = qisrc.worktree.GitWorkTree(worktree)
    return git_worktree


def get_git_projects(git_worktree, args):
    """ Get a list of git projects to use """
    if args.build_deps:
        # avoid circular deps
        import qibuild.parsers
        # FIXME: check that we have a toc object
        build_worktree = qibuild.worktree.open_build_worktree(git_worktree.worktree)
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

    def parse_one_arg(self, arg):
        # WorkTreeProjectParser.parse_one_arg only returns
        # a list of one element or raises
        worktree_projects = self.wt_parser.parse_one_arg(arg)
        worktree_project = worktree_projects[0]
        # closest git_project
        parent_git_project = qisys.parsers.find_parent_project(self.git_projects,
                                                               worktree_project.path)
        if parent_git_project:
            return [parent_git_project]


def GitBuildProjectParser:
    pass
