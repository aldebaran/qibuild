## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This package contains the QiDoc object."""

import itertools
import os
import sys
import webbrowser

import qisys
import qidoc.config

from qisys import ui

class QiDocBuilder:
    """A class to handle doc generation of several projects."""

    def __init__(self, projects, in_dir, out_dir=None):
        self.worktree = qisys.worktree.WorkTree(in_dir)
        self.projects, self.projects_to_build = projects, []

        self.templates_path, self.docs, self.in_dir = None, dict(), in_dir
        if not out_dir:
            self.out_dir = os.path.join(self.worktree.root, "build-doc")
        else:
            self.out_dir = qisys.sh.to_native_path(out_dir)

        self._load_doc_projects()
        self.doxytags_path = os.path.join(self.out_dir, "doxytags")

    def configure(self, opts, project=None):
        """Configure every projects.

        Always called before building anything.
        """
        if 'version' not in opts:
            raise VersionKeyMissingError(opts)

        qisys.sh.mkdir(self.doxytags_path, recursive=True)

        kwargs = {
            'doxytags_path': self.doxytags_path,
            'templates': self.templates_path,
            'doxylink': dict(),
        }
        if project is not None:
            if project not in self.docs:
                raise NoSuchProjectError(project)
            self.docs[project].configure(self.docs, opts, **kwargs)
            return
        for doc in self.docs.values():
            doc.configure(self.docs, opts, **kwargs)

    def build(self, opts, project=None):
        """Build everything."""
        self.configure(opts, project=project)

        # We don't check that project exists because configure method should
        # already have checked this.
        if project is not None:
            self.docs[project].build(self.docs, opts)
            return
        if len(self.projects) == len(self.docs.keys()):
            ui.warning('Building the whole worktree.')
        for doc in self.projects_to_build:
            self.docs[doc.name].build(self.docs, opts)

    def open(self, project=None):
        '''Opens a project in browser.'''
        out_dir = self.out_dir
        if project is not None:
            if project not in self.docs:
                raise NoSuchProjectError(project)
            out_dir = self.docs[project].dest
        if len(self.projects_to_build) == 1:
            out_dir = self.projects_to_build[0].dest
        elif len(self.projects) != len(self.worktree.projects):
            p_names = [p.name for p in self.projects_to_build]
            p_name = qisys.interact.ask_choice(p_names,
                                                 "Please choose in the following list")
            if p_name:
                out_dir = self.docs[p_name].dest
        index_html = os.path.join(out_dir, "index.html")
        if not os.path.exists(index_html):
            raise Exception("""\
Could not find an index.html in {out_dir}
Try running `qidoc build`""".format(out_dir=out_dir))
        ui.info("Opening", index_html, "in a web browser")
        if sys.platform == "darwin":
            index_html = "file://" + index_html
        webbrowser.open(index_html)

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
                if project.src in [prj.src for prj in self.projects]:
                    self.projects_to_build.append(doc)
            self.check_template(project.path, qiproj_xml)
        if not self.templates_path:
            raise NoTemplateRepositoryError()

    def _set_paths(self, worktree_project, doc_project):
        """Set src and dest attributes of the doc project."""
        src = os.path.join(worktree_project.path, doc_project.src)
        doc_project.src = qisys.sh.to_native_path(src)
        dest = os.path.join(self.out_dir, doc_project.dest)
        doc_project.dest = qisys.sh.to_native_path(dest)

    def check_template(self, p_path, qiproj_xml):
        """Check whether a project is a template project. If no templates
        project has been found yet, then set self.templates_path, else raise an
        exception.
        """
        is_template = qidoc.config.is_template(qiproj_xml)
        if not is_template:
            return
        if self.templates_path:
            raise TemplateProjectAlreadyExistsError(p_path, self.templates_path)
        self.templates_path = p_path

    def documentations_list(self):
        '''Returns a grouped list of documentations available and sorted, in
        tuples (documentation_type_name, documentations).'''
        keys, groups, grouper = [], [], lambda d: d.type_name()
        lst = sorted(self.projects_to_build)
        for key, group in itertools.groupby(lst, key=grouper):
            keys.append(key)
            groups.append(sorted(group))
        return zip(keys, groups)

    def is_in_project(self):
        return len(self.projects) != len(self.worktree.projects)


class ProjectNameCollisionError(Exception):
    '''When two projects have the same name.'''

    def __init__(self, project1, project2):
        Exception.__init__(self)
        self.project1, self.project2 = project1, project2

    def __str__(self):
        return """Two projects have the same name: {name}
First project is in: {path1} ({type1})
Second project is in: {path2} ({type2})
Please check your configuration.""".format(
            name = self.project1.name,
            path1 = self.project1.src, type1 = self.project1.type_name(),
            path2 = self.project2.src, type2 = self.project2.type_name(),
        )


class TemplateProjectAlreadyExistsError(Exception):
    '''There are two different projects for templates.'''

    def __init__(self, path, existing_path):
        Exception.__init__(self)
        self.path, self.existing_path = path, existing_path

    def __str__(self):
        return """Could not add project in {path} as a template repository.
There is already a template repository in {existing_path}.
Please check your configuration.""".format(
            path = self.path, existing_path = self.existing_path
        )


class NoTemplateRepositoryError(Exception):
    '''There is no template repository in documentation directory.'''

    def __str__(self):
        return '''Could not find any template repository.
Please make sure that one of the qiproject.xml looks like:
<qiproject template_repo="yes" />'''


class NoSuchProjectError(Exception):
    '''The project requested doesn't exist.'''

    def __init__(self, project):
        Exception.__init__(self)
        self.project = project

    def __str__(self):
        return 'No such project: {project}'.format(project = self.project)


class VersionKeyMissingError(Exception):
    '''Version key is not set in options for build.'''

    def __init__(self, opts):
        Exception.__init__(self)
        self.opts = opts

    def __str__(self):
        return '''Opts dictionary must at least contain a 'version' key.
It was containing the following keys: {keys}'''.format(
            keys = ', '.join(sorted(self.opts.keys()))
        )
