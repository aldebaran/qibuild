#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Handling maintainers in qiproject.xml files """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import locale
from xml.etree import ElementTree as etree

import qisys.qixml
from qisys import ui


class ProjectXML(qisys.qixml.XMLParser):
    """ ProjectXML Class """

    def _parse_maintainer(self, element):
        """ Parse Maintainer """
        maintainer = {'email': element.get('email'), 'name': element.text}
        self.target.append(maintainer)


def to_str(name=None, email=None):
    """ To Str """
    string = ""
    if name:
        string += name
    if name and email:
        string += " "
    if email:
        string += "<" + email + ">"
    return string


def get_xml_root(project):
    """ Get XML Root """
    return get_xml_tree(project).getroot()


def get_xml_tree(project):
    """ Get XML Tree """
    xml_path = project.qiproject_xml
    if not os.path.exists(xml_path):
        with open(xml_path, "w") as fp:
            fp.write("""<project version="3" />\n""")
    return qisys.qixml.read(xml_path)


def exists(project, name=None, email=None):
    """ Exists """
    maintainers = get(project)
    for maintainer in maintainers:
        if maintainer.get("name") == name and maintainer.get("email") == email:
            return True
    return False


def get(project, warn_if_none=False):
    """ Get """
    maintainers = list()
    project_xml = ProjectXML(maintainers)
    project_xml.parse(get_xml_root(project))
    if not maintainers and warn_if_none:
        mess = """\
The project in {src} has no maintainer.
Please add one or several <maintainer> tags in
{qiproject_xml} to silence this warning, like this:

<project version="3">
  <maintainer email="EMAIL">NAME</maintainer>
  ...
"""
        mess = mess.format(src=project.src, qiproject_xml=project.qiproject_xml)
        ui.warning(mess, end="")
    return maintainers


def remove(project, name=None, email=None):
    """ Remove """
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
    """ Clear """
    maintainers = get(project)
    if not maintainers:
        return False
    for maintainer in maintainers:
        remove(project, **maintainer)
    return True


def add(project, name=None, email=None):
    """ Add """
    if isinstance(name, str):
        name = name.decode("utf-8")
    if isinstance(email, str):
        email = email.decode("utf-8")
    if exists(project, name=name, email=email):
        return
    tree = get_xml_tree(project)
    root = tree.getroot()
    maint_elem = etree.Element("maintainer")
    maint_elem.set("email", email)
    maint_elem.text = name
    root.append(maint_elem)
    qisys.qixml.write(tree, project.qiproject_xml)
