## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" This package contains the QiDoc object

"""
import os

import qibuild
from qibuild.dependencies_solver import topological_sort
import qidoc.config
import qidoc.sphinx
import qidoc.doxygen



class QiDocBuilder:
    """ A class to handle doc generation of several
    projects

    """
    def __init__(self, in_dir, out_dir):
        self.worktree = qibuild.worktree.open_worktree(in_dir)
        self.in_dir = in_dir
        self.out_dir = out_dir

        self.templates_path = None
        self.sphinxdocs = dict()
        self.doxydocs = dict()

        # Will fill up self.templates_path, self.sphinxdocs and self.doxydocs
        self._load_doc_projects()
        self.deps_tree = self.get_deps_tree()

        if not self.templates_path:
            mess  = "Could not find any template repo\n"
            mess += "Please make sure that one of the qiproject.xml looks like:\n"
            mess += '<qiproject template_repo="yes" />\n'
            raise Exception(mess)
        self.doxytags_path = os.path.join(self.out_dir, "doxytags")

    def get_deps_tree(self):
        """ Get the tree of dependencies

        It is a dict {type:deps_tree} where
        type is 'sphinx' or 'doxygen', and
        deps_tree is a dict:
            {name:[dep names]}
        """
        doxy_tree = dict()
        sphinx_tree = dict()
        res = dict()
        for doxydoc in self.doxydocs.values():
            doxy_tree[doxydoc.name] = doxydoc.depends
        for sphinxdoc in self.sphinxdocs.values():
            sphinx_tree[sphinxdoc.name] = sphinxdoc.depends

        res["doxygen"] = doxy_tree
        res["sphinx"]  = sphinx_tree
        return res


    def build(self, opts):
        """ Main method: build everything

        """
        version = opts.get("version")
        if not version:
            raise Exception("opts dict must at least contain a 'version' key")

        qibuild.sh.mkdir(self.doxytags_path, recursive=True)
        doxylink = dict()

        doxydocs = self.sort_doxygen()
        for doxydoc in doxydocs:
            doxygen_mapping = self.get_doxygen_mapping(doxydoc.name)
            qidoc.doxygen.configure(doxydoc.src,
                    self.templates_path,
                    opts,
                    project_name=doxydoc.name,
                    doxytags_path=self.doxytags_path,
                    doxygen_mapping=doxygen_mapping)
            qidoc.doxygen.build(doxydoc.src, doxydoc.dest, opts)
            tag_file = os.path.join(self.doxytags_path, doxydoc.name + ".tag")
            # Store full path here because we'll need to compute
            # a relative path later
            doxylink[doxydoc.name] = (tag_file, doxydoc.dest)

        sphinxdocs = self.sort_sphinx()
        for sphinxdoc in sphinxdocs:
            intersphinx_mapping = self.get_intersphinx_mapping(sphinxdoc.name)
            qidoc.sphinx.configure(sphinxdoc.src, sphinxdoc.dest,
                self.templates_path,
                intersphinx_mapping,
                doxylink,
                opts)
            qidoc.sphinx.gen_download_zips(sphinxdoc.src)
            qidoc.sphinx.build(sphinxdoc.src, sphinxdoc.dest, opts)

    def sort_doxygen(self):
        """ Get a list of doxygen docs to build

        """
        deps_tree = self.deps_tree["doxygen"]
        doc_names = topological_sort(deps_tree, self.doxydocs.keys())
        return [self.get_doc("doxygen", d) for d in doc_names]

    def sort_sphinx(self):
        """ Get a list of sphinx docs to build, in the
        correct order

        """
        deps_tree = self.deps_tree["sphinx"]
        doc_names = topological_sort(deps_tree, self.sphinxdocs.keys())
        return [self.get_doc("sphinx", d) for d in doc_names]

    def get_intersphinx_mapping(self, name):
        """ Get the relevant intersphinx_mapping for
        the given name

        """
        res = dict()
        deps_tree = self.deps_tree["sphinx"]
        doc_names = topological_sort(deps_tree, [name])
        docs = [self.get_doc("sphinx", d) for d in doc_names]
        for doc in docs:
            # Remove self from the list:
            if doc.name != name:
                res[doc.name] = (doc.dest, None)
        return res

    def get_doxygen_mapping(self, name):
        """ Get the relevant Doxygen TAGFILES setting

        """
        doc = self.get_doc("doxygen", name)
        res = dict()
        deps_tree = self.deps_tree["doxygen"]
        dep_doc_names = topological_sort(deps_tree, [name])
        dep_docs = [self.get_doc("doxygen", d) for d in dep_doc_names]
        for dep_doc in dep_docs:
            # Remove self from the list
            if dep_doc.name == name:
                continue
            doxytag_file = os.path.join(self.doxytags_path,
                dep_doc.name + ".tag")
            dep_dest = dep_doc.dest
            rel_path = os.path.relpath(dep_dest, doc.dest)
            res[doxytag_file] = rel_path

        return res


    def get_doc(self, type_, name):
        """ Retun a qibuild.config.SphinxDoc or a
        qidoc.config.DoxyDoc object

        """
        if type_ == "doxygen":
            return self.doxydocs[name]
        if type_ == "sphinx":
            return self.sphinxdocs[name]

    def _load_doc_projects(self):
        """ Explore the qibuild projects, building the
        sphinxdocs and doxydocs attributes

        """
        for project in self.worktree.projects:
            qiproj_xml = os.path.join(project.src, "qiproject.xml")
            if not os.path.exists(qiproj_xml):
                continue
            (doxydocs, sphinxdocs) = qidoc.config.parse_project_config(qiproj_xml)
            # Fixup src, dest attributes:
            for doxydoc in doxydocs:
                doxydoc.src = os.path.join(project.src, doxydoc.src)
                doxydoc.dest = os.path.join(self.out_dir, doxydoc.dest)
                self.check_collision(doxydoc, "doxygen")
                self.doxydocs[doxydoc.name] = doxydoc
            for sphinxdoc in sphinxdocs:
                sphinxdoc.src = os.path.join(project.src, sphinxdoc.src)
                sphinxdoc.dest = os.path.join(self.out_dir, sphinxdoc.dest)
                self.check_collision(sphinxdoc, "sphinx")
                self.sphinxdocs[sphinxdoc.name] = sphinxdoc
            # Check if the project is a template project:
            self.check_template(project.name, project.src, qiproj_xml)


    def check_collision(self, project, doc_type):
        """" Check for collision between doc projects

        """
        name = project.name
        if doc_type == "doxygen":
            other_project = self.doxydocs.get(name)
        elif doc_type == "sphinx":
            other_project = self.sphinxdocs.get(name)

        if not other_project:
            return

        mess  = "Two %s projects have the same name: %s\n" % (doc_type, name)
        mess += "First project is in: %s\n" % other_project.src
        mess += "Other project is in: %s\n" % project.src
        mess += "Please check your configuration"
        raise Exception(mess)

    def check_template(self, p_name, p_path, qiproj_xml):
        """ Check whether a project is a template project
        If not templates project has been found yet, set
        self.templates_path, else raise an exception

        """
        is_template = qidoc.config.is_template(qiproj_xml)
        if is_template and  self.templates_path:
            mess  = "Could not add project %s from %s " (p_name, p_path)
            mess += "as a template repository.\n"
            mess += "There is already a template repository in %s\n" % self.templates_path
            mess += "Please check your configuration"
            raise Exception(mess)
        if is_template:
            self.templates_path = p_path



def find_qidoc_root(cwd=None):
    """ Find a qidoc root

    """
    if not cwd:
        cwd = os.getcwd()
    dirname = None
    while dirname or cwd:
        if os.path.exists(os.path.join(cwd, ".qi", "qibuild.xml")):
            return cwd
        (new_cwd, dirname) = os.path.split(cwd)
        if new_cwd == cwd:
            return
        cwd = new_cwd

def create_builder(worktree=None):
    """ Open a new QiDocBuilder using
    os.getcwd and looking for a qidoc.xml if root is None

    """
    if worktree is None:
        worktree = find_qidoc_root(os.getcwd())
        if not worktree:
            raise Exception("Could not find qidoc worktree")
    builder = QiDocBuilder(worktree)
    return builder

