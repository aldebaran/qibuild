import os
import difflib
import virtualenv

from qisys import ui
import qisys.worktree
import qisys.qixml

import qipy.project

class PythonWorkTree(qisys.worktree.WorkTreeObserver):
    def __init__(self, worktree):
        self.worktree = worktree
        self.python_projects = list()
        self._load_python_projects()
        self.config = "system"
        worktree.register(self)

    def on_project_added(self, project):
        """ Called when a new project has been registered """
        self._load_python_projects()

    def on_project_removed(self, project):
        """ Called when a project has been removed """
        self._load_python_projects()

    def on_project_moved(self, project):
        """ Called when a project has moved """
        self._load_python_projects()

    @property
    def root(self):
        return self.worktree.root

    def _load_python_projects(self):
        seen_names = dict()
        self.python_projects = list()
        for project in self.worktree.projects:
            setup_dot_py = os.path.join(project.path, "setup.py")
            qiproject_xml = os.path.join(project.path, "qiproject.xml")
            if not os.path.exists(qiproject_xml):
                continue
            if not os.path.exists(setup_dot_py):
                continue
            new_project = new_python_project(self, project)
            if not new_project:
                continue
            if new_project.name in seen_names:
                mess = """ \
Fond two project with the same name. (%s)
%s
%s
""" % (new_project.name, seen_names[project.src], new_project.src)
                raise Exception(mess)
            self.python_projects.append(new_project)
            seen_names[new_project.name] = new_project.src

    def get_python_project(self, name, raises=False):
        for project in self.python_projects:
            if project.name == name:
                return project
        if raises:
            result = {difflib.SequenceMatcher(a=name, b=x.name).ratio(): x.name for x in self.python_projects}
            mess = "No such python project: %s\n" % name
            mess += "Did you mean: %s?" % result[max(result)]
            raise Exception(mess)
        else:
            return None

    def bin_path(self, name):
        binaries_path = virtualenv.path_locations(self.venv_path)[-1]
        return os.path.join(binaries_path, name)

    @property
    def venv_path(self):
        res = os.path.join(self.worktree.dot_qi, "venvs", self.config)
        return res

    @property
    def pip(self):
        return self.bin_path("pip")

    @property
    def python(self):
        return self.bin_path("python")


def new_python_project(worktree, project):
    qiproject_xml = project.qiproject_xml
    tree = qisys.qixml.read(qiproject_xml)
    qipython_elem = tree.find("qipython")
    if qipython_elem is None:
        return
    name = qisys.qixml.parse_required_attr(qipython_elem, "name",
                                           xml_path=qiproject_xml)
    res = qipy.project.PythonProject(worktree, project.src, name)
    return res

