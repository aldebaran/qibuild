# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import os

import qidoc.doxygen


class TemplateProject(object):
    def __init__(self, doc_worktree, worktree_project):
        self.doc_type = "template"
        self.name = "template"
        self.depends = list()
        self.src = worktree_project.src
        self.path = worktree_project.path
        self.doc_worktree = doc_worktree

    @property
    def sphinx_conf(self):
        in_path = os.path.join(self.path,
                               "sphinx", "conf.in.py")
        if not os.path.exists(in_path):
            return ""
        with open(in_path, "r") as fp:
            return fp.read()

    @property
    def doxy_conf(self):
        in_path = os.path.join(self.path,
                               "doxygen", "Doxyfile.in")
        conf = qidoc.doxygen.read_doxyfile(in_path)
        filevars = [
            ("HTML_HEADER", "header.html"),
            ("HTML_FOOTER", "footer.html"),
            ("HTML_STYLESHEET", "doxygen.css")
        ]
        for (var, filename) in filevars:
            full_path = os.path.join(self.path, "doxygen", filename)
            if os.path.exists(full_path):
                conf[var] = full_path
            else:
                conf.pop(var, None)
        return conf

    @property
    def themes_path(self):
        return os.path.join(self.path, "sphinx", "_themes")

    def __repr__(self):
        return "<TemplateProject in %s>" % self.src
