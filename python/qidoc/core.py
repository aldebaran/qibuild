## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This package contains the QiDoc object."""

import itertools
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
# FIXME: dead code. from qibuild.dependencies_solver import topological_sort

class QiDocBuilder:
    """A class to handle doc generation of several projects."""

    def __init__(self, in_dir, out_dir="build-doc"):
        self.worktree = qisrc.worktree.open_worktree(in_dir)

        self.in_dir, self.out_dir = in_dir, out_dir
        self.templates_path, self.docs = None, dict()

        self._load_doc_projects()
        self.doxytags_path = os.path.join(self.out_dir, "doxytags")

    def configure_all(self, opts, project=None):
        """Configure every projects.

        Always called before building anything.
        """
        if 'version' not in opts:
            raise VersionKeyMissingError(opts)

        qibuild.sh.mkdir(self.doxytags_path, recursive=True)
        doxylink = dict()

        if project is not None:
            if project not in self.docs:
                raise NoSuchProjectError(project)
            self.docs[name].configure(opts)
            return
        for doc in self.docs.values():
            doc.configure(opts)

# FIXME: dead code
#        doxydocs = self.sort_doxygen()
#        for doxydoc in doxydocs:
#            doxygen_mapping = self.get_doxygen_mapping(doxydoc.name)
#            qidoc.doxygen.configure(doxydoc.src,
#                    self.templates_path,
#                    opts,
#                    project_name=doxydoc.name,
#                    doxytags_path=self.doxytags_path,
#                    doxygen_mapping=doxygen_mapping)
#
#            tag_file = os.path.join(self.doxytags_path, doxydoc.name + ".tag")
#            # Store full path here because we'll need to compute
#            # a relative path later
#            doxylink[doxydoc.name] = (tag_file, doxydoc.dest)
#
#        sphinxdocs = self.sort_sphinx()
#        for sphinxdoc in sphinxdocs:
#            intersphinx_mapping = self.get_intersphinx_mapping(sphinxdoc.name)
#            qidoc.sphinx.configure(sphinxdoc.src, sphinxdoc.dest,
#                self.templates_path,
#                intersphinx_mapping,
#                doxylink,
#                opts)
#            qidoc.sphinx.gen_download_zips(sphinxdoc.src)

    def build(self, opts, project=None):
        """Build everything."""
        self.configure(opts, project=project)

        # We don't check that project exists because configure method should
        # already have checked this.
        if project is not None:
            self.docs[name].build(opts)
            return

        for doc in self.docs.values():
            doc.build(opts)

# FIXME: dead code
#    def build_single(self, project, opts):
#        """Used to build a single project."""
#        if project not in self.docs:
#            raise NoSuchProjectError(project)
#        self.configure_all(opts)
#        self.docs[project].build(opts)

# FIXME: move this in qidoc.docs.{sphinx.SphinxDoc,doxygen.Doxygen}
#    def open_main(self):
#        """Used to open main doc. We assume one of the project as a dest
#        equals to `.`
#        """
#        index_html = os.path.join(self.out_dir, "index.html")
#        ui.info("Opening", index_html, "in a web browser")
#        if sys.platform == "darwin":
#            index_html = "file://" + index_html
#        webbrowser.open(index_html)
#
#    def open_single(self, project):
#        """ User to open a single doc."""
#        doc_proj = self.get_doc("sphinx", project)
#        if not doc_proj:
#            doc_proj = self.get_doc("doxygen", project)
#        if not doc_proj:
#            raise Exception("No such project: %s" % project)
#
#        index_html = os.path.join(doc_proj.dest, "index.html")
#        ui.info("Opening", index_html, "in a web browser")
#        if sys.platform == "darwin":
#            index_html = "file://" + index_html
#        webbrowser.open(index_html)

# FIXME: dead code.
#    def get_intersphinx_mapping(self, name):
#        """Get the relevant intersphinx_mapping for the given name."""
#        res = dict()
#        deps_tree = self.deps_tree["sphinx"]
#        doc_names = topological_sort(deps_tree, [name])
#        docs = [self.get_doc("sphinx", d) for d in doc_names]
#        for doc in docs:
#            # Remove self from the list:
#            if doc.name != name:
#                res[doc.name] = (doc.dest, None)
#        return res
#
#    def get_doxygen_mapping(self, name):
#        """Get the relevant Doxygen TAGFILES setting."""
#        doc = self.get_doc("doxygen", name)
#        res = dict()
#        deps_tree = self.deps_tree["doxygen"]
#        dep_doc_names = topological_sort(deps_tree, [name])
#        dep_docs = [self.get_doc("doxygen", d) for d in dep_doc_names]
#        for dep_doc in dep_docs:
#            # Remove self from the list
#            if dep_doc.name == name:
#                continue
#            doxytag_file = os.path.join(self.doxytags_path,
#                dep_doc.name + ".tag")
#            dep_dest = dep_doc.dest
#            rel_path = os.path.relpath(dep_dest, doc.dest)
#            res[doxytag_file] = rel_path
#        return res

    def _load_doc_projects(self):
        """Explore the qibuild projects, building the sphinxdocs and doxydocs
        attributes.
        """
        for project in self.worktree.projects:
            qiproj_xml = os.path.join(project.path, "qiproject.xml")
            if not os.path.exists(qiproj_xml):
                continue
            docs = qidoc.config.parse_project_config(qiproj_xml)
            for doc in docs:
                self._set_paths(project, doc)
                if doc.name in self.docs:
                    raise ProjectNameCollisionError(self.docs[doc.name], doc)
                self.docs[doc.name] = doc
                self.docs[doc.name].docs = self.docs
            self.check_template(project.path, qiproj_xml)
        if not self.templates_path:
            raise NoTemplateRepositoryError()

    def _set_paths(self, worktree_project, doc_project):
        """Set src and dest attributes of the doc project."""
        src = os.path.join(worktree_project.path, doc_project.src)
        doc_project.src = qibuild.sh.to_native_path(src)
        dest = os.path.join(self.out_dir, doc_project.dest)
        doc_project.dest = qibuild.sh.to_native_path(dest)

    def check_template(self, p_path, qiproj_xml):
        """Check whether a project is a template project. If no templates
        project has been found yet, then set self.templates_path, else raise an
        exception.
        """
        is_template = qidoc.config.is_template(qiproj_xml)
        if not is_template:
            return
        if self.templates_path:
            raise TemplateProjectAlreadyExistsError(p_path, self.template_path)
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

    def documentations_list(self):
        '''Returns a grouped list of documentations available and sorted, in
        tuples (documentation_type_name, documentations).'''
        keys, groups, grouper = [], [], lambda d: d.type_name()
        for k, g in itertools.groupby(sorted(self.docs.values()), key=grouper):
            keys.append(k)
            groups.append(sorted(g))
        return zip(keys, groups)


class ProjectNameCollisionError(Exception):
    def __init__(self, project1, project2):
        self.project1, self.project2 = project1, project2

    def __str__(self):
        return """Two {doc_type} projects have the same name: {name}
First project is in: {path1} ({type1})
Second project is in: {path2} ({type2})
Please check your configuration.""".format(
            name = self.project1.name,
            path1 = self.project1.path, type1 = self.project1.type_name(),
            path2 = self.project2.path, type2 = self.project2.type_name(),
        )


class TemplateProjectAlreadyExistsError(Exception):
    def __init__(self, path, existing_path):
        self.path, self.existing_path = path, existing_path

    def __str__(self):
        return """Could not add project in {path} as a template repository.
There is already a template repository in {existing_path}.
Please check your configuration.""".format(
            path = self.path, existing_path = self.existing_path
        )


class NoTemplateRepositoryError(Exception):
    def __str__(self):
        return '''Could not find any template repository.
Please make sure that one of the qiproject.xml looks like:
<qiproject template_repo="yes" />'''


class NoSuchProjectError(Exception):
    def __init__(self, project):
        self.project = project

    def __str__(self):
        return 'No such project: {project}'.format(project = project)


class VersionKeyMissingError(Exception):
    def __init__(self, opts):
        self.opts = opts

    def __str__(self):
        return '''Opts dictionary must at least contain a 'version' key.
It was containing the following keys: {keys}'''.format(
            keys = ', '.join(sorted(self.opts.keys()))
        )
