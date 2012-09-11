## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling qidoc config files

"""

import qixml
from xml.etree import ElementTree as etree

class Depends:
    def __init__(self):
        self.name = None

    def parse(self, element):
        self.name = element.get("name")

class SphinxDoc:
    def __init__(self):
        self.name = None
        self.src = None
        self.dest = None
        self.depends = list()

    def parse(self, element):
        self.name = qixml.parse_required_attr(element, "name")
        self.src  = element.get("src", ".")
        self.dest = element.get("dest", self.name)
        depends_elements = element.findall("depends")
        for depends_element in depends_elements:
            depends = Depends()
            depends.parse(depends_element)
            self.depends.append(depends.name)

class DoxyDoc:
    def __init__(self):
        self.name = None
        self.src = None
        self.dest = None
        self.depends = list()

    def parse(self, element):
        self.name = qixml.parse_required_attr(element, "name")
        self.src = element.get("src", ".")
        self.dest = element.get("dest", self.name)
        depends_elements = element.findall("depends")
        for depends_element in depends_elements:
            depends = Depends()
            depends.parse(depends_element)
            self.depends.append(depends.name)


def parse_project_config(config_path):
    """Parse a config file, returns a  tuple of lists (SphinxDoc, DoxyDoc)."""
    tree = etree.ElementTree()
    try:
        tree.parse(config_path)
    except Exception, e:
        mess  = "Could not parse config from %s\n" % config_path
        mess += "Error was: %s" % e
        raise Exception(mess)
    root = tree.getroot()
    doxydocs = list()
    doxy_trees = root.findall("doxydoc")
    for doxy_tree in doxy_trees:
        doxydoc = DoxyDoc()
        doxydoc.parse(doxy_tree)
        doxydocs.append(doxydoc)
    sphinxdocs = list()
    sphinx_trees = root.findall("sphinxdoc")
    for sphinx_tree in sphinx_trees:
        sphinxdoc = SphinxDoc()
        sphinxdoc.parse(sphinx_tree)
        sphinxdocs.append(sphinxdoc)
    return (doxydocs, sphinxdocs)

def is_template(qiproj_xml):
    """Check whether a project is a template repo."""
    tree = etree.ElementTree()
    tree.parse(qiproj_xml)
    root = tree.getroot()
    return root.get("template_repo", "")  in ["true", "1"]
