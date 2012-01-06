## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling qidoc config files

"""

import os
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
        self.name = element.get("name")
        self.src  = element.get("src")
        dest = element.get("dest")
        if dest is None:
            self.dest = self.name
        else:
            self.dest = dest
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
        self.name = element.get("name")
        self.src  = element.get("src")
        dest = element.get("dest")
        if dest is None:
            self.dest = self.name
        else:
            self.dest = dest
        depends_elements = element.findall("depends")
        for depends_element in depends_elements:
            depends = Depends()
            depends.parse(depends_element)
            self.depends.append(depends.name)

class DoxygenTemplates:
    def __init__(self):
        self.doxyfile = None
        self.css = None
        self.header = None
        self.footer = None

    def parse(self, element):
        self.doxyfile = element.get("doxyfile")
        self.css = element.get("css")
        self.header = element.get("header")
        self.footer = element.get("footer")

class SphinxTemplates:
    def __init__(self):
        self.config = None
        self.themes = None

    def parse(self, element):
        self.config = element.get("config")
        self.themes = element.get("themes")


class Templates:
    def __init__(self):
        self.repo = None

    def parse(self, element):
        self.repo = element.get("repo")

class Defaults:
    def __init__(self):
        self.root_project = None

    def parse(self, element):
        self.root_project = element.get("root_project")

class QiDocConfig:
    def __init__(self):
        self.defaults = Defaults()
        self.templates = Templates()

    def parse(self, element):
        defaults_tree = element.find("defaults")
        if defaults_tree is not None:
            self.defaults = Defaults()
            self.defaults.parse(defaults_tree)

        template_tree = element.find("templates")
        if template_tree is not None:
            self.templates = Templates()
            self.templates.parse(template_tree)

def parse_qidoc_config(config_path):
    """ Parse a config file, returns a
    QiDoc object

    """
    tree = etree.ElementTree()
    try:
        tree.parse(config_path)
    except Exception, e:
        mess  = "Could not parse config from %s\n" % config_path
        mess += "Error was: %s" % e
        raise Exception(mess)
    res = QiDocConfig()
    root = tree.getroot()
    res.parse(root)
    return res

def parse_project_config(config_path):
    """ Parse a config file, returns a  tuple
    of lists (SphinxDoc, DoxyDoc)

    """
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
        doxydoc = SphinxDoc()
        doxydoc.parse(doxy_tree)
        doxydocs.append(doxydoc)
    sphinxdocs = list()
    sphinx_trees = root.findall("sphinxdoc")
    for sphinx_tree in sphinx_trees:
        sphinxdoc = SphinxDoc()
        sphinxdoc.parse(sphinx_tree)
        sphinxdocs.append(sphinxdoc)
    return (doxydocs, sphinxdocs)
