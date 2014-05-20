""" Run a python script from the virtualenv"""

import os

from qisys import ui
import qisys.interact
import qisys.parsers
import qibuild.parsers
import qipy.parsers

def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="*")

def do(args):
    build_worktree = qibuild.parsers.get_build_worktree(args)
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    worktree = build_worktree.worktree

    venvs_path = os.path.join(worktree.dot_qi,
                             "venvs")
    name = build_config.build_directory("py")
    venv_root = os.path.join(venvs_path, name)
    if not os.path.exists(venv_root):
        err = "No Virtualenv found in %s\n" % (venv_root)
        err += "Tring running `qipy configure`"
        raise Exception(err)

    python_bin = os.path.join(venv_root, "bin", "python")
    qisys.command.call([python_bin] + args.command)
