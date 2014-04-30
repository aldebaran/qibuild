""" Install all python projects """
import os
import sys

from qisys import ui
import qisys.command

import qisys.parsers
import qipy.parsers

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("dest")

def do(args):
    dest = args.dest
    python_worktree = qipy.parsers.get_python_worktree(args)
    python_projects = python_worktree.python_projects
    for project in python_projects:
        ui.info(ui.green, " * ", ui.blue, project.src)
        setup_py = os.path.join(project.path, "setup.py")
        cmd = [sys.executable, setup_py, "install", "--root", dest,
               '--prefix=']
        qisys.command.call(cmd, cwd=project.path)
    # Also install a python wrapper so that everything goes smoothly
    to_write="""\
#!/bin/bash
SDK_DIR=$(dirname "$(readlink -f $0 2>/dev/null)")
export LD_LIBRARY_PATH=${SDK_DIR}/lib
export PYTHONPATH=${SDK_DIR}/lib/python2.7/site-packages/
python "$@"
"""
    python_wrapper = os.path.join(dest, "python")
    with open(python_wrapper, "w") as fp:
        fp.write(to_write)
    os.chmod(python_wrapper, 0755)
