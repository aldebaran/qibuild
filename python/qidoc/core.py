## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" This package contains the QiDoc object

"""
import os

import qibuild
import qidoc.config
import qidoc.sphinx
import qidoc.doxygen


class QiDocBuilder:
    """ A class to handle doc generation of several
    projects

    All repositories must be relative to a qidoc.xml
    file
    """
    def __init__(self, in_dir, out_dir):
        self.in_dir = in_dir
        self.out_dir = out_dir
        self.cfg_path = os.path.join(in_dir, "qidoc.xml")
        self.config = qidoc.config.parse(self.cfg_path)
        # Sanity checks
        for repo in self.config.repos:
            repo_path = os.path.join(self.in_dir, repo.name)
            if not os.path.exists(repo_path):
                mess  = "Invalid config file: %s" % self.cfg_path
                mess += "Could not find repo: %s" % repo_path
                mess += "(%s does not exist)" % repo_path
                raise Exception(mess)

        templates_repo = self.config.templates.repo
        templates_path = os.path.join(self.in_dir, templates_repo)
        if not os.path.exists(templates_path):
            mess  = "Invalid config file: %s " % self.cfg_path
            mess += "Could not find templates repo: %" % templates_repo
            mess += "(%s does not exist)" % templates_path
            raise Exception(mess)
        self.templates_path = templates_path


    def build(self, opts):
        """ Main method: build everything for every
        repository

        """
        version = opts.get("version")
        doxytags_path = os.path.join(self.out_dir, "doxytags")
        qibuild.sh.mkdir(doxytags_path, recursive=True)
        doxylink = dict()
        if not version:
            raise Exception("opts dict must at least contain a 'version' key")
        for repo in self.config.repos:
            repo_path = os.path.join(self.in_dir, repo.name)
            for doxydoc in repo.doxydocs:
                doxy_src  = os.path.join(repo_path, doxydoc.src)
                doxy_dest = os.path.join(self.out_dir, doxydoc.dest)
                qidoc.doxygen.configure(doxy_src, self.templates_path,
                    opts,
                    project_name=doxydoc.name)
                qidoc.doxygen.build(doxy_src, doxy_dest)
                tag_file = qidoc.doxygen.gen_tag_file(doxy_src, doxydoc.name, doxytags_path)
                doxylink[doxydoc.name] = (tag_file, doxydoc.dest)

        opts["doxylink"] = str(doxylink)

        for repo in self.config.repos:
            repo_path = os.path.join(self.in_dir, repo.name)
            for sphinxdoc in repo.sphinxdocs:
                sphinx_src = os.path.join(repo_path, sphinxdoc.src)
                sphinx_dest = os.path.join(self.out_dir, sphinxdoc.dest)
                qidoc.sphinx.configure(sphinx_src, self.templates_path, opts)
                qidoc.sphinx.build(sphinx_src, sphinx_dest)


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

