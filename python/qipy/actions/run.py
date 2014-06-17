""" Run a python script from the virtualenv"""

import os
import subprocess
import virtualenv

from qisys import ui
import qisys.interact
import qisys.parsers
import qibuild.parsers
import qipy.parsers

def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("--list", action="store_true", dest="dolist", default=False, help="List all available binaries in the virtualenv")
    parser.add_argument("command", metavar="COMMAND", nargs="*")

def do(args):
    build_worktree = qibuild.parsers.get_build_worktree(args)
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    worktree = build_worktree.worktree
    cmd = args.command

    venvs_path = os.path.join(worktree.dot_qi,
                             "venvs")
    name = build_config.build_directory("py")
    venv_root = os.path.join(venvs_path, name)
    if not os.path.exists(venv_root):
        err = "No Virtualenv found in %s\n" % (venv_root)
        err += "Please run `qipy bootstrap`"
        raise Exception(err)

    binaries_path = virtualenv.path_locations(venv_root)[-1]

    if args.dolist:
        for f in sorted(os.listdir(binaries_path)):
            if os.path.isfile(os.path.join(binaries_path, f)):
                print f
        return

    if not cmd:
        cmd = [os.path.join(venv_root, binaries_path, "ipython")]
    else:
        if os.path.exists(cmd[0]):
            bin_in_venv = None
        else:
            bin_in_venv = os.path.join(venv_root, binaries_path, cmd[0])
        if bin_in_venv and os.path.exists(bin_in_venv):
            cmd[0] = bin_in_venv
        else:
            cmd = [os.path.join(venv_root, binaries_path, "python")] + cmd
    ui.debug("Calling", cmd)
    subprocess.check_call(cmd)
