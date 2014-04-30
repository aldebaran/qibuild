""" Run a python script from the virtualenv"""

import os

from qisys import ui
import qisys.interact
import qisys.parsers
import qibuild.parsers
import qipy.parsers

def configure_parser(parser):
    qibuild.parsers.build_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="+")

def do(args):
    build_worktree = qibuild.parsers.get_build_worktree(args)
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    build_worktree.build_config = build_config
    worktree = build_worktree.worktree
    config = build_config.active_config
    if not config:
        config = "system"

    venvs_path = os.path.join(worktree.dot_qi, "venvs")
    venv_root = os.path.join(venvs_path, config)
    if not os.path.exists(venv_root):
        err = "No Virtualenv found for config '%s'\n" % config
        err += "Tring running `qipy setup`"
        raise Exception(err)

    python_bin = os.path.join(venv_root, "bin", "python")
    qisys.command.call([python_bin] + args.command)

