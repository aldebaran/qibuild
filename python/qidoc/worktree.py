import os
import posixpath

from qisys import ui
import qisys.worktree
import qisys.qixml

from qidoc.sphinx_project import SphinxProject
from qidoc.doxygen_project import DoxygenProject
from qidoc.template_project import TemplateProject


class DocWorkTree(qisys.worktree.WorkTreeObserver):
    """ Stores configuration of doxygen and sphinx projects """
    def __init__(self, worktree):
        self.worktree = worktree
        self.root = worktree.root
        self.doc_projects = list()
        self._load_doc_projects()
        worktree.register(self)

    def _load_doc_projects(self):
        self.doc_projects = list()
        for worktree_project in self.worktree.projects:
            doc_project = new_doc_project(self, worktree_project)
            if doc_project:
                if not isinstance(doc_project, TemplateProject):
                    self.check_unique_name(doc_project)
                self.doc_projects.append(doc_project)

    @property
    def template_project(self):
        res = [x for x in self.doc_projects if isinstance(x, TemplateProject)]
        if not res:
            return None
        if len(res) > 1:
            mess = "Found multiple template projects\n"
            for project in res:
                mess += "  * " + project.path + "\n"
            raise Exception(mess)
        return res[0]

    def on_project_added(self, project):
        """ Called when a new project has been registered """
        self._load_doc_projects()

    def on_project_removed(self, project):
        """ Called when a build project has been removed """
        self._load_doc_projects()

    def get_doc_project(self, name, raises=False):
        for project in self.doc_projects:
            if isinstance(project, TemplateProject):
                continue
            if project.name == name:
                return project
        if raises:
            raise Exception("No such doc project: %s" % name)
        else:
            return None

    def check_unique_name(self, new_project):
        """ Return a boolean telling if we should add the project
        to the worktree

        """
        project_with_same_name = self.get_doc_project(new_project.name,
                                                      raises=False)
        # maybe the new project comes from qibuild2 compat ...
        if project_with_same_name:
            raise Exception("""\
Found two projects with the same name ({0})
In:
* {1}
* {2}
    """.format(new_project.name,
               project_with_same_name.path,
               new_project.path))

    def __repr__(self):
        return "<DocWorkTree in %s>" % self.root


def new_doc_project(doc_worktree, project):
    qiproject_xml = project.qiproject_xml
    if not os.path.exists(qiproject_xml):
        return None
    tree = qisys.qixml.read(project.qiproject_xml)
    root = tree.getroot()
    if root.get("version") == "3":
        return _new_doc_project_3(doc_worktree, project)
    else:
        return _new_doc_project_2(doc_worktree, project)

def new_template_project(doc_worktree, project):
    qiproject_xml = project.qiproject_xml
    if not os.path.exists(qiproject_xml):
        return None
    tree = qisys.qixml.read(project.qiproject_xml)
    root = tree.getroot()
    if root.get("version") == "3":
        return


def _new_doc_project_3(doc_worktree, project):
    qiproject_xml = project.qiproject_xml
    tree = qisys.qixml.read(qiproject_xml)
    root = tree.getroot()
    qidoc_elem = root.find("qidoc")
    doc_type = qidoc_elem.get("type")
    if doc_type is None:
        raise BadProjectConfig(qiproject_xml,
                               "Expecting a 'type' attribute")
    return _new_doc_project(doc_worktree, project, qidoc_elem, doc_type)


def _new_doc_project_2(doc_worktree, project):
    """ Parse qidoc2 syntax in case the 'src' attribute is not used,
    else warn and suggest using `qidoc convert-worktree`

    """
    # There is no way to be retro-compatible unless we parse
    # the 'src' attributes of 'spinxdoc' and 'doxygen' tags
    # in qisys.WorkTree ...
    qiproject_xml = project.qiproject_xml
    tree = qisys.qixml.read(qiproject_xml)
    root = tree.getroot()

    if qisys.qixml.parse_bool_attr(root, "template_repo"):
        return TemplateProject(doc_worktree, project)

    doc_elems = root.findall("sphinxdoc")
    doc_elems.extend(root.findall("doxydoc"))

    if not doc_elems:
        return

    if len(doc_elems) > 1:
        ui.warning("Deprecated configuration detected", "\n",
                   "(in %s)" % qiproject_xml, "\n",
                   "Having several docs in the same qiproject.xml is "
                   "no longer supported", "\n",
                   "Please run qidoc convert-worktree")
        return
    doc_elem = doc_elems[0]
    if doc_elem.get("src") is not None:
        ui.warning("Deprecated configuration detected", "\n",
                   "(in %s)" % qiproject_xml, "\n",
                   "The 'src' attribute is no longer supported", "\n",
                   "Please run qidoc convert-worktree")

    if doc_elem.tag == "sphinxdoc":
        doc_type = "sphinx"
    else:
        doc_type = "doxygen"
    return _new_doc_project(doc_worktree, project, doc_elem, doc_type)

def _new_doc_project(doc_worktree, project, xml_elem, doc_type):
    qiproject_xml = project.qiproject_xml
    if doc_type == "template":
        return TemplateProject(doc_worktree, project)

    name = xml_elem.get("name")
    if not name:
        raise BadProjectConfig(qiproject_xml,
                               "Expecting a 'name' attribute")
    doc_project = None
    if doc_type == "sphinx":
        doc_project = SphinxProject(doc_worktree, project, name)
    elif doc_type == "doxygen":
        doc_project = DoxygenProject(doc_worktree, project, name)
    else:
        raise BadProjectConfig(qiproject_xml,
                               "Unknow doc type: %s", doc_type)

    depends_elem = xml_elem.findall("depends")
    for depend_elem in depends_elem:
        dep_name = depend_elem.get("name")
        if not dep_name:
            raise BadProjectConfig(qiproject_xml,
                                   "<depends> must have a 'name' attribute")
        doc_project.depends.append(depend_elem.get("name"))
    return doc_project


class BadProjectConfig(Exception):
    def __str__(self):
        return """
Incorrect configuration detected for project in {0}
{1}
""".format(*self.args)
