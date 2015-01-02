## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Handling maintainers in git notes."""

import os
from xml.etree import ElementTree as etree

import qisrc.git
import qisys.qixml


class ProjectXML(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(ProjectXML, self).__init__(target)

    def _parse_maintainer(self, element):
        maintainer = {'email': element.get('email'), 'name': element.text}
        self.target.append(maintainer)

def to_str(name=None, email=None):
    string = ""
    if name:
        string += name
    if name and email:
        string += " "
    if email:
        string += "<" + email + ">"
    return string

def get_xml_root(project):
    tree = get_xml_tree(project)
    return tree.getroot()

def get_xml_tree(project):
    xml_path = project.qiproject_xml
    if not os.path.exists(xml_path):
        with open(xml_path, "w") as fp:
            fp.write("""<project version="3" />\n""")
    tree = qisys.qixml.read(xml_path)
    return tree

def exists(project, name=None, email=None):
    maintainers = get(project)

    for maintainer in maintainers:
        if maintainer.get("name") == name and maintainer.get("email") == email:
            return True

    return False

def get(project):
    maintainers = list()
    project_xml = ProjectXML(maintainers)
    project_xml.parse(get_xml_root(project))
    return maintainers

def remove(project, name=None, email=None):
    if not exists(project, name=name, email=email):
        return False

    tree = get_xml_tree(project)
    root = tree.getroot()
    for elem in root.findall("./maintainer[@email='"+email+"']"):
        if elem.text == name:
            root.remove(elem)

    qisys.qixml.write(tree, project.qiproject_xml)
    return True


def clear(project):
    maintainers = get(project)
    if len(maintainers) == 0:
        return False
    for maintainer in maintainers:
        remove(project, **maintainer)
    return True


def add(project, name=None, email=None):
    if exists(project, name=name, email=email):
        return
    tree = get_xml_tree(project)
    root = tree.getroot()
    maint_elem = etree.Element("maintainer")
    maint_elem.set("email", email)
    maint_elem.text = name
    root.append(maint_elem)
    qisys.qixml.write(tree, project.qiproject_xml)

