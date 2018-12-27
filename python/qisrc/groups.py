#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Qisrc Groups """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import xml.etree.ElementTree as etree

import qisys.qixml


class Groups(object):
    """ Groups Class """

    def __init__(self):
        """ Groups Init """
        self.groups = dict()
        self.default_group = None

    @property
    def group_names(self):
        """ Group Names """
        return self.groups.keys()

    def projects(self, group):
        """ Projects """
        return self.subgroups_group(group)

    def configure_group(self, name, projects, default=False):
        """ Configure Group """
        group = Group(name)
        if default:
            group.default = True
        group.projects = projects
        self.groups[name] = group

    def remove_group(self, name):
        """ Remove Group """
        self.groups.pop(name, None)

    def subgroups_group(self, group_name, projects=None):
        """ SubGroups Group """
        if projects is None:
            projects = list()
        group = self.groups.get(group_name)
        if group is None:
            raise GroupError("No such group: %s" % group_name)
        projects.extend(group.projects)
        for subgroup in group.subgroups:
            self.subgroups_group(subgroup, projects=projects)
        return projects


class GroupsParser(qisys.qixml.XMLParser):
    """ GroupsParser Class """

    def __init__(self, target):
        """ GroupsParser Init """
        super(GroupsParser, self).__init__(target)
        self._ignore = ["group_names"]

    def _parse_group(self, element):
        """ Parse Group """
        group_name = element.attrib['name']
        group = Group(group_name)
        parser = GroupParser(group)
        parser.parse(element)
        self.target.groups[group.name] = group
        default = qisys.qixml.parse_bool_attr(element, "default", default=False)
        if default:
            self.target.default_group = group

    def _write_groups(self, element):
        """ Write Group """
        for group in self.target.groups.values():
            parser = GroupParser(group)
            element.append(parser.xml_elem())


class Group(object):
    """ Group Class """

    def __init__(self, name):
        """ Group Init """
        self.name = name
        self.default = False
        self.subgroups = list()
        self.projects = list()


class GroupParser(qisys.qixml.XMLParser):
    """ GroupParser Class """

    def _parse_project(self, element):
        """ Parse Project """
        self.target.projects.append(element.attrib['name'])

    def _parse_group(self, element):
        """ Parse Group """
        self.target.subgroups.append(element.attrib['name'])

    def _write_subgroups(self, element):
        """ Write SubGroups """
        for subgroup in self.target.subgroups:
            parser = GroupParser(subgroup)
            element.append(parser.xml_elem())

    def _write_projects(self, element):
        """ Write Projects """
        for project in self.target.projects:
            project_elem = qisys.qixml.etree.Element("project")
            project_elem.set("name", project)
            element.append(project_elem)


def get_root(worktree):
    """ Get Root """
    manifest_file = os.path.join(worktree.root, ".qi", "manifests", "default", "manifest.xml")
    if not os.path.exists(manifest_file):
        return None
    tree = etree.parse(manifest_file)
    root = tree.getroot()
    groups_elem = root.find("groups")
    if groups_elem is None:
        return None
    return groups_elem


def get_groups(worktree):
    """ Get Groups """
    root = get_root(worktree)
    if root is None:
        return None
    groups = Groups()
    parser = GroupsParser(groups)
    parser.parse(root)
    return groups


class GroupError(Exception):
    """ GroupError Exception """
    pass
