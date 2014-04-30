import os
import difflib

from qisys import ui
import qisys.worktree
import qisys.qixml


class PythonWorkTree():
    def __init__(self, worktree):
        self.worktree = worktree
        self.python_projects = list()
        self.load_python_projects()

    @property
    def root(self):
        return self.worktree.root

    def load_python_projects(self):
        self.python_projects = list()
        for project in self.worktree.projects:
            setup_dot_py = os.path.join(project.path, "setup.py")
            qiproject_xml = os.path.join(project.path, "qiproject.xml")
            if not os.path.exists(qiproject_xml):
                continue
            if os.path.exists(setup_dot_py):
                self.python_projects.append(project)

    def venv_path(self, name):
        res = os.path.join(self.worktree.dot_qi, "venvs", name)
        return res

