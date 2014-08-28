""" Rebase repositories on top of an other branch of the manifest

"""

from qisys import ui
import qisys.parsers
import qisrc.parsers
import qisrc.rebase

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("--branch")
    parser.add_argument("--push", action="store_true",
                        help="Push the rebased branch. Warning! Uses push -f")
    parser.add_argument("--undo", action="store_true",
                        help="Undo the previous push")
    parser.add_argument("--dry-run", action="store_true",
                        help="Dry run")
    parser.set_defaults(push=False, dry_run=False)

def do(args):
    branch = args.branch
    push = args.push
    undo = args.undo
    dry_run = args.dry_run
    if undo and branch:
        raise Exception("Cannot use --undo with --branch")
    if not undo and not branch:
        raise Exception("Argument --branch is required")

    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=False,
                                                  use_build_deps=True)

    qisrc.rebase.rebase_worktree(git_worktree, git_projects, branch,
                                 push=push, undo=undo, dry_run=dry_run)
