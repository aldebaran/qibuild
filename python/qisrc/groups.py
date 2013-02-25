import os

import xml.etree.ElementTree as etree

import qisys.qixml

from qisys import ui

class Groups(qisys.qixml.RootXMLParser):
    def __init__(self, root):
        super(Groups, self).__init__(root)
        self.groups = dict()

    def _parse_group(self, element):
        group_name = element.attrib['name']
        group = Group(element, group_name)
        group.parse()
        self.groups[group.name] = group

    def projects(self, group_name):
        return self.subgroups_group(group_name)

    def subgroups_group(self, group_name, projects=None):
        if projects is None:
            projects = list()

        group = self.groups.get(group_name)
        if group is None:
            ui.debug(ui.green, group_name, ui.reset, "is not a known group.")
            return projects

        projects.extend(group.projects)

        for subgroup in group.subgroups:
            self.subgroups_group(subgroup, projects=projects)

        return projects

class Group(qisys.qixml.RootXMLParser):
    def __init__(self, root, name):
        super(Group, self).__init__(root)
        self.name = name
        self.subgroups = list()
        self.projects = list()

    def _parse_project(self, element):
        self.projects.append(element.attrib['name'])

    def _parse_group(self, element):
        self.subgroups.append(element.attrib['name'])

def get_root(worktree):
    file = os.path.join(worktree.root, ".qi", "groups.xml")
    if not os.path.exists(file):
        return None
    tree = etree.parse(file)
    return tree.getroot()

def get_groups(worktree):
    root = get_root(worktree)
    if root is None:
        return None
    groups = Groups(root)
    groups.parse()
    return groups
