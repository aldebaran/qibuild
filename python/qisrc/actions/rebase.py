""" Rebase repositories on top of an other branch of the manifest

"""

from qisys import ui
import qisys.parsers
import qisrc.parsers
import qisrc.rebase

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("branch")
    parser.add_argument("--push", action="store_true",
                        help="Push the rebased branch. Warning! Uses push -f")
    parser.add_argument("--undo", action="store_true",
                        help="Undo the previous push")
    parser.set_defaults(push=False, force=False)

def do(args):
    branch = args.branch
    push = args.push
    undo = args.undo

    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=False)

    qisrc.rebase.rebase_worktree(git_worktree, git_projects, branch,
                                 push=push, undo=undo)
