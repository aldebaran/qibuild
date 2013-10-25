""" Checkout a new manifest branch and every repository
in the worktree

"""

from qisys import ui
import qisrc.parsers

import sys

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    group = parser.add_argument_group("checkout options")
    group.add_argument("branch")
    group.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Discard local changes. Use with caution")
    parser.set_defaults(force=False)

def do(args):
    branch = args.branch
    git_worktree = qisrc.parsers.get_git_worktree(args)
    for manifest in git_worktree.manifests.values():
        name = manifest.name
        groups = manifest.groups
        branch = args.branch
        git_worktree.configure_manifest(name, manifest.url,
                                        groups=groups, branch=branch)
        git_worktree.checkout(name, branch, force=args.force)

