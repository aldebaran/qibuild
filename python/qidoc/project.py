## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import abc
import os

import qisys.sh

class DocProject(object):

    __metaclass__ = abc.ABCMeta
    doc_type = None

    def __init__(self, doc_worktree, project, name, depends=None, dest=None):
        self.doc_worktree = doc_worktree
        self.name = name
        self.src = project.src
        self.path = project.path
        if not depends:
            depends = list()
        if not dest:
            dest = self.name
        self.depends = list()
        self.prebuild_script = None
        self.translated = False
        self.linguas = list()
        self._html_dir = None
        self._dest = dest
        self._is_base_project = False

    @property
    def is_base_project(self):
        return self._is_base_project

    @is_base_project.setter
    def is_base_project(self, value):
        self._is_base_project = value
        if self._is_base_project:
            self._dest = "."

    @property
    def qiproject_xml(self):
        return os.path.join(self.path, "qiproject.xml")

    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, value):
        self._dest = value

    @abc.abstractmethod
    def configure(self, **kwargs):
        pass

    @abc.abstractmethod
    def build(self, **kwargs):
        pass

    @abc.abstractmethod
    def install(self, destdir):
        pass

    def clean(self):
        qisys.sh.rm(self.build_dir)

    @property
    def build_dir(self):
        build_dir = os.path.join(self.path, "build-doc")
        qisys.sh.mkdir(build_dir)
        return build_dir

    @property
    def html_dir(self):
        if self._html_dir is None:
            self._html_dir = os.path.join(self.build_dir, "html")
        res = self._html_dir
        qisys.sh.mkdir(res, recursive=True)
        return res

    @html_dir.setter
    def html_dir(self, value):
        self._html_dir = value

    @property
    def index_html(self):
        return os.path.join(self.html_dir, "index.html")

    @property
    def template_project(self):
        return self.doc_worktree.template_project

    @property
    def doxydeps(self):
        res = list()
        for dep_name in self.depends:
            doc_project = self.doc_worktree.get_doc_project(dep_name, raises=False)
            if doc_project and doc_project.doc_type == "doxygen":
                res.append(doc_project)
        return res

    def append_doxy_xml_path(self, paths):
        for doxydep in self.doxydeps:
            doxypath = os.path.join(doxydep.build_dir, 'xml')
            if not doxypath in paths:
                paths.append(doxypath)
            doxydep.append_doxy_xml_path(paths)

    def __repr__(self):
        return "<%s %s in %s>" % (self.doc_type.capitalize() + "Project",
                                  self.name, self.src)

    def __eq__(self, other):
        return self.doc_type == other.doc_type and \
                self.src == other.src and \
                self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)
