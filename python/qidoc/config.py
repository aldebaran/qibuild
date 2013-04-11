## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Handling qidoc config files."""

from qidoc.docs.doxygen import DoxygenDoc
from qidoc.docs.sphinx import SphinxDoc
from xml.etree import ElementTree as etree

def _get_by_documentation_type(root, tree_name, doc_class, docs):
    '''Browse a path to find specific type of documentation.'''
    for tree in root.findall(tree_name):
        docs.append(doc_class(tree))

def parse_project_config(config_path):
    """Parse a config file, returns a  tuple of lists (SphinxDoc, DoxyDoc)."""
    tree = etree.ElementTree()
    try:
        tree.parse(config_path)
    except Exception, err:
        mess  = "Could not parse config from %s\n" % config_path
        mess += "Error was: %s" % err
        raise Exception(mess)
    root, docs = tree.getroot(), []
    _get_by_documentation_type(root, 'doxydoc', DoxygenDoc, docs)
    _get_by_documentation_type(root, 'sphinxdoc', SphinxDoc, docs)
    return docs

def is_template(qiproj_xml):
    """Check whether a project is a template repo."""
    tree = etree.ElementTree()
    tree.parse(qiproj_xml)
    root = tree.getroot()
    return root.get("template_repo", "") in ["true", "1"]
