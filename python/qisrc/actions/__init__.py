## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" qisrc actcions """

import os
import qisys.actions
import qisrc.worktree


class NotInAGitRepo(Exception):
    """ Custom exception when user did not
    specify any git repo ond the command line
    and we did not manage to guess one frome the
    working dir

    """
    def __str__(self):
        return """ Could not guess git repository from current working directory
  Here is what you can do :
     - try from a valid git repository
     - specify a repository path on the command line
"""

def get_git_worktree(args):
    """ Get a git worktree to use """
    worktree = qisys.actions.get_worktree(args)
    git_worktree = qisrc.worktree.GitWorkTree(worktree)
    return git_worktree


def get_git_projects(git_worktree, args):
    """ Get a list of git projects """
    import ipdb; ipdb.set_trace()
    repo_paths = []
    if not args.projects:
        repo_path = qisrc.git.get_repo_root(os.getcwd())
        if not repo_path:
            raise NotInAGitRepo()
        repo_paths = [repo_path]
    else:
        repo_paths = args.projects


def _get_git_project(worktree, project_arg)
    """ Helper for get_git_projects """
    # First, assume it's a path
    # (like in:  cd foo; qisrc push .)
    as_path = qisys.sh.to_native_path(project_arg)
    if os.path.exists(as_path):
        project = worktree.get_project(as_path, raises=False)
        if project:
            return project
    # Then, assume it's a project source
    # (like in:  cd bar; qisrc pu foo)

