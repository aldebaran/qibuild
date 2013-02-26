""" Common tools for actions

"""

import os
import qisys.worktree



def get_worktree(args):
    """ Get a worktree right after argument parsing.

    If --worktree was not given, try to guess it from
    the current working directory

    """
    wt_root = args.worktree
    if not wt_root:
        wt_root = qisys.worktree.guess_worktree(raises=True)
    return qisys.worktree.open_worktree(wt_root)

def get_projects(args):
    """ Get a list of worktree projects from the command line """
    res = list()
    if not args.projects:

