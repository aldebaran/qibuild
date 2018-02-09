# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Run a python script from the virtualenv"""

import os
import virtualenv

from qisys import ui
import qisys.interact
import qisys.parsers
import qibuild.parsers
import qipy.parsers


def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("--list", action="store_true", dest="dolist",
                        default=False,
                        help="List all available binaries in the virtualenv")
    parser.add_argument("--no-exec", dest="exec_", action="store_false",
                        help="Do not use os.execve (Mostly useful for tests")
    parser.add_argument("command", metavar="COMMAND", nargs="*")
    parser.set_defaults(exec_=True)


def do(args):
    build_worktree = qibuild.parsers.get_build_worktree(args)
    env = build_worktree.get_env()
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
        cmd = ["ipython"]

    if os.path.exists(cmd[0]):
        # Assume it is a script we want to run
        python_path = os.path.join(binaries_path, "python")
        cmd.insert(0, python_path)
    else:
        script_path = qipy.venv.find_script(venv_root, cmd[0])
        if script_path:
            cmd[0] = script_path

    lib_path = virtualenv.path_locations(venv_root)[1]
    env["PYTHONHOME"] = venv_root
    env["PYTHONPATH"] = os.path.join(lib_path, "site-packages")

    if args.exec_:
        ui.debug("exec", cmd)
        os.execve(cmd[0], cmd, env)
    else:
        qisys.command.call(cmd, env=env)
