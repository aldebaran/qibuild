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



class QiDocBuilder(qibuild.worktree.WorkTree):
    """ A class to handle doc generation of several
    projects

    """
    def __init__(self, in_dir, out_dir):
        qibuild.worktree.WorkTree.__init__(self, in_dir)
        self.in_dir = in_dir
        self.out_dir = out_dir
        self.cfg_path = os.path.join(in_dir, "qidoc.xml")
        self.config = qidoc.config.parse_qidoc_config(self.cfg_path)

        templates_repo = self.config.templates.repo
        templates_path = os.path.join(self.in_dir, templates_repo)
        if not os.path.exists(templates_path):
            mess  = "Invalid config file: %s " % self.cfg_path
            mess += "Could not find templates repo: %" % templates_repo
            mess += "(%s does not exist)" % templates_path
            raise Exception(mess)
        self.templates_path = templates_path

        self.doxytags_path = os.path.join(self.out_dir, "doxytags")

        self.sphinxdocs = dict()
        self.doxydocs = dict()
        self._load_doc_projects()
        self.deps_tree = self.get_deps_tree()


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
            qidoc.doxygen.build(doxydoc.src, doxydoc.dest)
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
            qidoc.sphinx.build(sphinxdoc.src, sphinxdoc.dest)

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
        for (p_name, p_path) in self.buildable_projects.iteritems():
            qiproj_xml = os.path.join(p_path, "qiproject.xml")
            (doxydocs, sphinxdocs) = qidoc.config.parse_project_config(qiproj_xml)
            # Fixup src, dest attributes:
            for doxydoc in doxydocs:
                doxydoc.src = os.path.join(p_path, doxydoc.src)
                doxydoc.dest = os.path.join(self.out_dir, doxydoc.dest)
                self.doxydocs[doxydoc.name] = doxydoc
            for sphinxdoc in sphinxdocs:
                sphinxdoc.src = os.path.join(p_path, sphinxdoc.src)
                sphinxdoc.dest = os.path.join(self.out_dir, sphinxdoc.dest)
                self.sphinxdocs[sphinxdoc.name] = sphinxdoc


def find_qidoc_root(cwd=None):
    """ Find a qidoc root

    """
    if not cwd:
        cwd = os.getcwd()
    dirname = None
    while dirname or cwd:
        if os.path.exists(os.path.join(cwd, "qidoc.xml")):
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

