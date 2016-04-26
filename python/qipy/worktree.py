## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import difflib
import virtualenv

from qisys import ui
import qisys.error
import qisys.worktree
import qisys.qixml

import qipy.project

class PythonWorkTree(qisys.worktree.WorkTreeObserver):
    """ Container for Python projects """
    def __init__(self, worktree, config="system"):
        self.worktree = worktree
        self.python_projects = list()
        self._load_python_projects()
        self.config = config
        worktree.register(self)

    def reload(self):
        self._load_python_projects()

    @property
    def root(self):
        return self.worktree.root

    def _load_python_projects(self):
        seen_names = dict()
        self.python_projects = list()
        for project in self.worktree.projects:
            qiproject_xml = os.path.join(project.path, "qiproject.xml")
            if not os.path.exists(qiproject_xml):
                continue
            new_project = new_python_project(self, project)
            if not new_project:
                continue
            if new_project.name in seen_names:
                mess = """ \
Found two projects with the same name. (%s)
%s
%s
""" % (new_project.name, seen_names[new_project.name], new_project.src)
                raise qisys.error.Error(mess)
            self.python_projects.append(new_project)
            seen_names[new_project.name] = new_project.src

    def get_python_project(self, name, raises=False):
        """ Get a Python project given its name """
        for project in self.python_projects:
            if project.name == name:
                return project
        if raises:
            mess = ui.did_you_mean("No such python project: %s" % name,
                                         name, [x.name for x in self.python_projects])
            raise qisys.worktree.NoSuchProject(name, mess)
        else:
            return None

    def bin_path(self, name, win_extension=".exe"):
        """ Path to the virtualenv's binaries """
        binaries_path = virtualenv.path_locations(self.venv_path)[-1]
        res = os.path.join(binaries_path, name)
        if os.name == "nt":
            res += win_extension
        return res

    @property
    def venv_path(self):
        """ Path to the virtualenv """
        res = os.path.join(self.worktree.dot_qi, "venvs",
                           self.config)
        return res

    @property
    def pip(self):
        """ Path to the pip binary """
        return self.bin_path("pip")

    @property
    def python(self):
        """ Path to the python executable in the virtualenv """
        return self.bin_path("python")

    def activate_this(self):
        """ Activate this virtualenv """
        activate_this_dot_py = self.bin_path("activate_this.py")
        execfile(activate_this_dot_py, { "__file__" : activate_this_dot_py })


def new_python_project(worktree, project):
    qiproject_xml = project.qiproject_xml
    tree = qisys.qixml.read(qiproject_xml)
    qipython_elem = tree.find("qipython")
    if qipython_elem is None:
        return
    name = qisys.qixml.parse_required_attr(qipython_elem, "name",
                                           xml_path=qiproject_xml)
    python_project = qipy.project.PythonProject(worktree, project.src, name)
    script_elems = qipython_elem.findall("script")
    for script_elem in script_elems:
        src = qisys.qixml.parse_required_attr(script_elem, "src",
                                              xml_path=qiproject_xml)
        script = qipy.project.Script(src)
        python_project.scripts.append(script)

    module_elems = qipython_elem.findall("module")
    for module_elem in module_elems:
        src = module_elem.get("src", "")
        name = qisys.qixml.parse_required_attr(module_elem, "name",
                                              xml_path=qiproject_xml)
        module = qipy.project.Module(name, src)
        module.qimodule = qisys.qixml.parse_bool_attr(module_elem, "qimodule")
        python_project.modules.append(module)


    package_elems = qipython_elem.findall("package")
    for package_elem in package_elems:
        name = qisys.qixml.parse_required_attr(package_elem, "name",
                                              xml_path=qiproject_xml)
        src = package_elem.get("src", "")
        package = qipy.project.Package(name, src)
        package.qimodule = qisys.qixml.parse_bool_attr(package_elem, "qimodule")
        python_project.packages.append(package)

    setup_elem = qipython_elem.find("setup")
    if setup_elem is not None:
        python_project.setup_with_distutils = \
            qisys.qixml.parse_bool_attr(setup_elem, "with_distutils")

    return python_project
