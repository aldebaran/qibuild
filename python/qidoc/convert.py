#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import posixpath

import qisys.qixml


def convert_project(project):
    """
    Convert a qidoc2 project so it's still usable in qidoc2 and qidoc3.
    :returns: True if a conversion happened
    """
    if not os.path.exists(project.qiproject_xml):
        return False
    qiproject_xml = project.qiproject_xml
    tree = qisys.qixml.read(qiproject_xml)
    root_elem = tree.getroot()
    if root_elem.get("version") == "3":
        return False
    if qisys.qixml.parse_bool_attr(root_elem, "template_repo"):
        convert_template_project(project)
        return False
    doc_elems = root_elem.findall("sphinxdoc")
    doc_elems.extend(root_elem.findall("doxydoc"))
    if not doc_elems:
        return False
    for doc_elem in doc_elems:
        handle_src_attribute(project, root_elem, doc_elem)
    qisys.qixml.write(root_elem, qiproject_xml)
    return True


def handle_src_attribute(project, root_elem, doc_elem):
    """ Handle Src Attribute """
    worktree = project.worktree
    src = doc_elem.get("src")
    if not src:
        return
    if src == ".":
        del doc_elem.attrib["src"]
        return
    subproject_src = posixpath.join(project.src, src)
    subproject = worktree.get_project(subproject_src)
    if subproject:
        subproject_path = subproject.path
    else:
        subproject_path = create_sub_project(worktree, root_elem, project, src)
    create_doc_project(worktree, subproject_path, doc_elem)
    root_elem.remove(doc_elem)


def convert_template_project(_project):
    """ Convert Template Project """
    pass


def create_sub_project(_worktree, root_elem, project, src):
    """ Create Sub Project """
    project_elem = qisys.qixml.etree.Element("project")
    project_elem.set("src", src)
    root_elem.append(project_elem)
    return os.path.join(project.path, src)


def create_doc_project(_worktree, project_path, doc_elem):
    """ Create Doc Project """
    doc_type = None
    if doc_elem.tag == "doxydoc":
        doc_type = "doxygen"
    elif doc_elem.tag == "sphinxdoc":
        doc_type = "sphinx"
    new_doc_elem = qisys.qixml.etree.Element("qidoc")
    new_doc_elem.set("type", doc_type)
    new_doc_elem.set("name", doc_elem.get("name"))
    dest = doc_elem.get("dest")
    if dest:
        new_doc_elem.set("dest", dest)
    for depend_elem in doc_elem.findall("depends"):
        new_doc_elem.append(depend_elem)
    qiproject_xml = os.path.join(project_path, "qiproject.xml")
    qisys.qixml.write(new_doc_elem, qiproject_xml)
    project_elem = qisys.qixml.etree.Element("project")
    project_elem.set("version", "3")
    project_elem.append(new_doc_elem)
    qisys.qixml.write(project_elem, qiproject_xml)
