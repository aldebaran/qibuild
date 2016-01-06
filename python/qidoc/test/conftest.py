## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import bs4

from qisys.test.conftest import *
import qisys.qixml

import qidoc.worktree

class TestDocWorkTree(qidoc.worktree.DocWorkTree):
    """ A subclass of DocWorkTree that can create doc projects """

    def __init__(self, worktree=None):
        if not worktree:
            worktree = TestWorkTree()
        super(TestDocWorkTree, self).__init__(worktree)

    def add_templates(self):
        self.add_test_project("templates")

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1101
        return py.path.local(self.root)

    def create_doc_project(self, name, src=None,
                           depends=None, doc_type="sphinx",
                           dest=None):
        if not depends:
            depends = list()
        if not src:
            src = name
        proj_path = self.tmpdir.join(*src.split("/"))
        proj_path.ensure(dir=True)
        project_elem = qisys.qixml.etree.Element("project")
        project_elem.set("version", "3")
        qidoc_elem = qisys.qixml.etree.Element("qidoc")
        qidoc_elem.set("name", name)
        qidoc_elem.set("type", doc_type)
        project_elem.append(qidoc_elem)
        for dep_name in depends:
            dep_elem = qisys.qixml.etree.Element("depends")
            dep_elem.set("name", dep_name)
            qidoc_elem.append(dep_elem)
        if dest:
            qidoc_elem.set("dest", dest)
        qiproject_xml = proj_path.join("qiproject.xml").strpath
        qisys.qixml.write(project_elem, qiproject_xml)
        self.worktree.add_project(src)
        return self.get_doc_project(name)

    def create_sphinx_project(self, name, src=None, depends=None):
        return self.create_doc_project(name, src=src, depends=depends,
                                       doc_type="sphinx")
    def create_doxygen_project(self, name, src=None, depends=None):
        return self.create_doc_project(name, src=src, depends=depends,
                                       doc_type="doxygen")

    def add_test_project(self, src):
        """ Copy a project, reading sources from qidoc/test/projects

        Can return None when testing qidoc2 retro-compat
        """
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)

        worktree_project = self.worktree.add_project(src)
        doc_project = qidoc.worktree.new_doc_project(self, worktree_project)
        return doc_project

class QiDocAction(TestAction):
    def __init__(self):
        super(QiDocAction, self).__init__("qidoc.actions")
        self.doc_worktree = TestDocWorkTree()

    def add_test_project(self, *args, **kwargs):
        return self.doc_worktree.add_test_project(*args, **kwargs)

    def create_sphinx_project(self, *args, **kwargs):
        return self.doc_worktree.create_sphinx_project(*args, **kwargs)

    def create_doxygen_project(self, *args, **kwargs):
        return self.doc_worktree.create_doxygen_project(*args, **kwargs)


def find_link(html_path, text):
    with open(html_path, "r") as fp:
        data = fp.read()
    soup = bs4.BeautifulSoup(data)
    link = soup.find("a", text=text)
    target = link.attrs["href"]
    target_path = target.split("#")[0]
    return target_path


# pylint: disable-msg=E1101
@pytest.fixture
def doc_worktree(cd_to_tmpdir):
    return TestDocWorkTree()

# pylint: disable-msg=E1103
@pytest.fixture
def qidoc_action(cd_to_tmpdir):
    res = QiDocAction()
    return res
