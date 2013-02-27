""" Common tools for actions

"""

import os
import qisys.worktree
from qisys.parsers import WorkTreeProjectParser



def get_worktree(args):
    """ Get a worktree right after argument parsing.

    If --worktree was not given, try to guess it from
    the current working directory

    """
    wt_root = args.worktree
    if not wt_root:
        wt_root = qisys.worktree.guess_worktree(raises=True)
    return qisys.worktree.open_worktree(wt_root)

def get_projects(worktree, args):
    """ Get a list of worktree projects from the command line """
    parser = WorkTreeProjectParser(worktree)
    return parser.parse_args(args)
