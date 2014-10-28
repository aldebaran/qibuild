import sys
import os
import qisys.remote
import subprocess

from qisys import ui
from qisys.abstractbuilder import AbstractBuilder
import qisys.command
import qipy.venv
from qibuild.project import write_qi_path_conf

class PythonBuilder(AbstractBuilder):
    """
    configure : make sources available for developement
      (create a virtualenv and run pip install -e .)
    make : no-op
    install : just copy the python lib. If there are
    extensions written in CMake, they will be installed by the
    CMakeBuilder

    """
    def __init__(self, python_worktree, build_worktree=None):
        self.python_worktree = python_worktree
        self.build_worktree = build_worktree
        self.projects = list()

    @property
    def config(self):
        return self.python_worktree.config

    def bootstrap(self, remote_packages=None, site_packages=True):
        qipy.venv.configure_virtualenv(self.config,
                                       self.python_worktree,
                                       build_worktree=self.build_worktree,
                                       remote_packages=remote_packages,
                                       site_packages=site_packages)
        qi_path_sdk_dirs = [p.sdk_directory for p in self.build_worktree.build_projects]
        write_qi_path_conf(self.python_worktree.venv_path, qi_path_sdk_dirs)

    def configure(self, *args, **kwargs):
        pass

    def build(self, *args, **kwargs):
        pass

    def install(self, dest, *args, **kwargs):
        n = len(self.projects)
        for i, project in enumerate(self.projects):
            ui.info_count(i, n, ui.green, "Installing",
                          ui.reset, ui.blue, project.name)
            setup_py = os.path.join(project.path, "setup.py")
            python = self.python_worktree.python
            if not os.path.exists(python):
                raise Exception("Please call `qipy bootstrap`")
            subprocess.check_call([python, setup_py, "install",
                                   "--root", dest, "--prefix=."],
                                   cwd=project.path)
        # Also install a python wrapper so that everything goes smoothly
        to_write="""\
#!/bin/bash
SDK_DIR=$(dirname "$(readlink -f $0 2>/dev/null)")
export LD_LIBRARY_PATH=${SDK_DIR}/lib
export PYTHONPATH=${SDK_DIR}/lib/python2.7/site-packages/
exec python "$@"
"""
        python_wrapper = os.path.join(dest, "python")
        with open(python_wrapper, "w") as fp:
            fp.write(to_write)
        os.chmod(python_wrapper, 0755)

    def deploy(self, url):
        with qisys.sh.TempDir() as tmp:
            self.install(tmp)
            qisys.remote.deploy(tmp, url)
