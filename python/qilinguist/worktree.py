#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.qixml
import qisys.worktree
from qisys import ui


class LinguistWorkTree(qisys.worktree.WorkTreeObserver):
    """ LinguistWorkTree Class """

    def __init__(self, worktree):
        """ LinguistWorkTree Init """
        self.worktree = worktree
        self.root = worktree.root
        self.linguist_projects = list()
        self._load_linguist_projects()
        worktree.register(self)

    def _load_linguist_projects(self):
        """ Load Linguist Projects """
        self.linguist_projects = list()
        for worktree_project in self.worktree.projects:
            linguist_project = new_linguist_project(self, worktree_project)
            if linguist_project:
                self.check_unique_name(linguist_project)
                self.linguist_projects.append(linguist_project)

    def reload(self):
        """ Reload """
        self._load_linguist_projects()

    def get_linguist_project(self, name, raises=False):
        """ Get Linguits Project """
        for project in self.linguist_projects:
            if project.name == name:
                return project
        if raises:
            mess = ui.did_you_mean("No such linguist project: %s" % name,
                                   name, [x.name for x in self.linguist_projects])
            raise qisys.worktree.NoSuchProject(name, mess)
        else:
            return None

    def check_unique_name(self, new_project):
        """ Check Unique Name """
        project_with_same_name = self.get_linguist_project(new_project.name,
                                                           raises=False)
        if project_with_same_name:
            raise Exception(
                """Found two projects with the same name ({0})\nIn:\n* {1}\n* {2}\n""".format(
                    new_project.name,
                    project_with_same_name.path,
                    new_project.path
                )
            )


def new_linguist_project(_linguist_worktree, project):
    """ New Linguist Project """
    if not os.path.exists(project.qiproject_xml):
        return None
    tree = qisys.qixml.read(project.qiproject_xml)
    root = tree.getroot()
    if root.get("version") != "3":
        return None
    elem = root.find("qilinguist")
    if elem is None:
        # try deprecated name too
        elem = root.find("translate")
        if elem is None:
            return None
    name = elem.get("name")
    if not name:
        raise BadProjectConfig(project.qiproject_xml, "Expecting a 'name' attribute")
    domain = elem.get("domain")
    if not domain:
        domain = name
    linguas = elem.get("linguas").split()
    if not linguas:
        linguas = ["en_US"]
    tr_framework = elem.get("tr")
    if not tr_framework:
        raise BadProjectConfig(project.qiproject_xml, "Expecting a 'tr' attribute")
    if tr_framework not in ["linguist", "gettext"]:
        mess = """ \
Unknow translation framework: {}.
Choose between 'linguist' or 'gettext'
"""
        raise BadProjectConfig(mess.format(tr_framework))
    if tr_framework == "linguist":
        from qilinguist.qtlinguist import QtLinguistProject
        new_project = QtLinguistProject(name, project.path, domain=domain,
                                        linguas=linguas)
    else:
        from qilinguist.qigettext import GettextProject
        new_project = GettextProject(name, project.path, domain=domain,
                                     linguas=linguas)
    return new_project


class BadProjectConfig(Exception):
    """ BadProjectConfig Exception """

    def __str__(self):
        """ String Representation """
        return """\nIncorrect configuration detected for project in {0}\n{1}\n""".format(*self.args)
