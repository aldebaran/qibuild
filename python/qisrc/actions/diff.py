""" Display diff with an other branch of the worktree """

import qisys.parsers
import qisrc.parsers
import qisrc.diff

def configure_parser(parser):
    qisys.parsers.project_parser(parser)
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("branch")

def do(args):
    branch = args.branch
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=True)
    qisrc.diff.diff_worktree(git_worktree, git_projects, branch,
                             cmd=["diff", "--stat"])
