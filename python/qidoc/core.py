## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This package contains the QiDoc object."""

import os
import pprint
import sys
import webbrowser

import qibuild
import qidoc.config
import qidoc.doxygen
import qidoc.sphinx
import qisrc

from qibuild import ui
from qibuild.dependencies_solver import topological_sort

class QiDocBuilder:
    """A class to handle doc generation of several projects."""

    def __init__(self, in_dir, out_dir="build-doc"):
        self.worktree = qisrc.worktree.open_worktree(in_dir)
        self.in_dir = in_dir
        self.out_dir = out_dir
        # Set during configure_all()
        self.opts = dict()

        self.templates_path = None
        self.sphinxdocs = dict()
        self.doxydocs = dict()

        # Will fill up self.templates_path, self.sphinxdocs and self.doxydocs
        self._load_doc_projects()
        self.deps_tree = self.get_deps_tree()
        ui.debug("QiDocBuilder dep tree: ", pprint.pformat(self.deps_tree))

        if not self.templates_path:
            mess  = "Could not find any template repo\n"
            mess += "Please make sure that one of the qiproject.xml looks like:\n"
            mess += '<qiproject template_repo="yes" />\n'
            raise Exception(mess)
        self.doxytags_path = os.path.join(self.out_dir, "doxytags")

    def get_deps_tree(self):
        """Get the tree of dependencies

        It is a dict {type:deps_tree} where type is 'sphinx' or 'doxygen', and
        deps_tree is a dict: {name:[dep names]}
        """
        doxy_tree = dict()
        sphinx_tree = dict()
        res = dict()
        for doxydoc in self.doxydocs.values():
            doxy_tree[doxydoc.name] = doxydoc.depends
            # Check that every dep exists:
            for dep in doxydoc.depends:
                if self.get_doc("doxygen", dep) is None:
                    mess  = "Could not find doxygen doc dep: %s\n" % dep
                    mess += "(brought by: %s)" % doxydoc.name
                    ui.warning(mess)
                    doxydoc.depends.remove(dep)

        for sphinxdoc in self.sphinxdocs.values():
            sphinx_tree[sphinxdoc.name] = sphinxdoc.depends
            # Check that every dep exists:
            for dep in sphinxdoc.depends:
                if self.get_doc("sphinx", dep) is None:
                    mess  = "Could not find sphinx doc dep %s\n" % dep
                    mess += "(brought by: %s)" % sphinxdoc.name
                    ui.warning(mess)
                    sphinxdoc.depends.remove(dep)

        res["doxygen"] = doxy_tree
        res["sphinx"]  = sphinx_tree
        return res

    def configure_all(self, opts):
        """Configure every projects.

        Always called before building anything.
        """
        version = opts.get("version")
        if not version:
            raise Exception("opts dict must at least contain a 'version' key")

        self.opts = opts.copy()
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

    def build_all(self, opts):
        """Build everything."""
        self.configure_all(opts)
        doxydocs = self.sort_doxygen()
        for doxydoc in doxydocs:
            qidoc.doxygen.build(doxydoc.src, doxydoc.dest, opts)
        sphinxdocs = self.sort_sphinx()
        for sphinxdoc in sphinxdocs:
            qidoc.sphinx.build(sphinxdoc.src, sphinxdoc.dest, opts)


    def build_single(self, project, opts):
        """Used to build a single project."""
        sphinx = self.get_doc("sphinx", project)
        doxy   = self.get_doc("doxygen", project)

        if sphinx is None and doxy is None:
            raise Exception("No such project: %s" % project)

        self.configure_all(opts)

        if sphinx:
            qidoc.sphinx.build(sphinx.src, sphinx.dest, opts)
        if doxy:
            qidoc.doxygen.build(doxy.src, doxy.dest, opts)


    def open_main(self):
        """Used to open main doc. We assume one of the project as a dest
        equals to `.`
        """
        index_html = os.path.join(self.out_dir, "index.html")
        print "Opening", index_html, "in a web browser"
        if sys.platform == "darwin":
            index_html = "file://" + index_html
        webbrowser.open(index_html)

    def open_single(self, project):
        """ User to open a single doc

        """

        doc_proj = self.get_doc("sphinx", project)
        if not doc_proj:
            doc_proj = self.get_doc("doxygen", project)
        if not doc_proj:
            raise Exception("No such project: %s" % project)

        index_html = os.path.join(doc_proj.dest, "index.html")
        print "Opening", index_html, "in a web browser"
        if sys.platform == "darwin":
            index_html = "file://" + index_html
        webbrowser.open(index_html)

    def sort_doxygen(self):
        """Get a list of doxygen docs to build."""
        deps_tree = self.deps_tree["doxygen"]
        doc_names = topological_sort(deps_tree, self.doxydocs.keys())
        res = [self.get_doc("doxygen", d) for d in doc_names]
        return res

    def sort_sphinx(self):
        """Get a list of sphinx docs to build, in the correct order."""
        deps_tree = self.deps_tree["sphinx"]
        doc_names = topological_sort(deps_tree, self.sphinxdocs.keys())
        res = [self.get_doc("sphinx", d) for d in doc_names]
        return res

    def get_intersphinx_mapping(self, name):
        """Get the relevant intersphinx_mapping for the given name."""
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
        """Get the relevant Doxygen TAGFILES setting."""
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
        """
        Retun a qibuild.config.SphinxDoc or a qidoc.config.DoxyDoc object.
        """
        if type_ == "doxygen":
            return self.doxydocs.get(name)
        if type_ == "sphinx":
            return self.sphinxdocs.get(name)

    def _load_doc_projects(self):
        """Explore the qibuild projects, building the sphinxdocs and doxydocs
        attributes.
        """
        for project in self.worktree.projects:
            qiproj_xml = os.path.join(project.path, "qiproject.xml")
            if not os.path.exists(qiproj_xml):
                continue
            (doxydocs, sphinxdocs) = qidoc.config.parse_project_config(qiproj_xml)
            # Fixup src, dest attributes:
            for doxydoc in doxydocs:
                self.set_paths(project, doxydoc)
                self.check_collision(doxydoc, "doxygen")
                self.doxydocs[doxydoc.name] = doxydoc
            for sphinxdoc in sphinxdocs:
                self.set_paths(project, sphinxdoc)
                self.check_collision(sphinxdoc, "sphinx")
                self.sphinxdocs[sphinxdoc.name] = sphinxdoc
            # Check if the project is a template project:
            self.check_template(project.path, qiproj_xml)


    def set_paths(self, worktree_project, doc_project):
        """Set src and dest attributes of the doc project."""
        src = os.path.join(worktree_project.path, doc_project.src)
        doc_project.src = qibuild.sh.to_native_path(src)
        dest = os.path.join(self.out_dir, doc_project.dest)
        doc_project.dest = qibuild.sh.to_native_path(dest)

    def check_collision(self, project, doc_type):
        """Check for collision between doc projects,"""
        name = project.name
        if doc_type == "doxygen":
            other_project = self.doxydocs.get(name)
        elif doc_type == "sphinx":
            other_project = self.sphinxdocs.get(name)

        if not other_project:
            return

        mess  = "Two %s projects have the same name: %s\n" % (doc_type, name)
        mess += "First project is in: %s\n" % other_project.path
        mess += "Other project is in: %s\n" % project.path
        mess += "Please check your configuration"
        raise Exception(mess)

    def check_template(self, p_path, qiproj_xml):
        """Check whether a project is a template project. If no templates
        project has been found yet, then set self.templates_path, else raise an
        exception.
        """
        is_template = qidoc.config.is_template(qiproj_xml)
        if not is_template:
            return
        if self.templates_path:
            mess  = "Could not add project in %s" % (p_path)
            mess += "as a template repository.\n"
            mess += "There is already a template repository in %s\n" % self.templates_path
            mess += "Please check your configuration"
            raise Exception(mess)
        self.templates_path = p_path

    def project_from_cwd(self, cwd=None):
        """Get a doc project name from the current working dir"""
        if not cwd:
            cwd = os.getcwd()

        for doxydoc in self.doxydocs.values():
            if doxydoc.src in cwd:
                return doxydoc.name
        for sphinxdoc in self.sphinxdocs.values():
            if sphinxdoc.src in cwd:
                return sphinxdoc.name


def find_qidoc_root(cwd=None):
    """Find a qidoc root"""
    if not cwd:
        cwd = os.getcwd()
    dirname = None
    while dirname or cwd:
        if os.path.exists(os.path.join(cwd, ".qi", "worktree.xml")):
            return cwd
        (new_cwd, dirname) = os.path.split(cwd)
        if new_cwd == cwd:
            return
        cwd = new_cwd

def create_builder(worktree=None):
    """Open a new QiDocBuilder using os.getcwd and looking for a qidoc.xml if
    root is None.
    """
    if worktree is None:
        worktree = find_qidoc_root(os.getcwd())
        if not worktree:
            raise Exception("Could not find qidoc worktree")
    builder = QiDocBuilder(worktree)
    return builder

