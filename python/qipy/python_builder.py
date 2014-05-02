import sys
import os

from qisys import ui
from qisys.abstractbuilder import AbstractBuilder
import qisys.command
import qipy.venv

class PythonBuilder(AbstractBuilder):
    """
    configure : make sources available for developement
      (create a virtualenv and run pip install -e .)
    make : no-op
    install : just copy the python lib. If there are
    extensions written in CMake, they will be installed by the
    CMakeBuilder

    """
    def __init__(self, python_worktree, build_worktree):
        self.python_worktree = python_worktree
        self.build_worktree = build_worktree
        self.projects = list()

    def configure(self, *args, **kwargs):
        qipy.venv.configure_virtualenv(self.python_worktree, self.build_worktree)

    def build(self, *args, **kwargs):
        pass

    def install(self, dest, *args, **kwargs):
        for project in self.projects:
            ui.info(ui.green, " * ", ui.blue, project.name)
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
