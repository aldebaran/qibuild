## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling qidoc config files

"""

from xml.etree import ElementTree as etree

class SphinxDoc:
    def __init__(self):
        self.name = None
        self.src = None
        self.dest = None

    def parse(self, element):
        self.name = element.get("name")
        self.src  = element.get("src")
        dest = element.get("dest")
        if dest is None:
            self.dest = self.name
        else:
            self.dest = dest

class DoxyDoc:
    def __init__(self):
        self.name = None
        self.src = None
        self.dest = None

    def parse(self, element):
        self.name = element.get("name")
        self.src  = element.get("src")
        dest = element.get("dest")
        if dest is None:
            self.dest = self.name
        else:
            self.dest = dest

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

class Repo:
    def __init__(self):
        self.name = None
        self.sphinxdocs = list()
        self.doxydocs   = list()

    def parse(self, element):
        self.name = element.get("name")
        sphinx_trees = element.findall("sphinxdoc")
        for sphinx_tree in sphinx_trees:
            sphinxdoc = SphinxDoc()
            sphinxdoc.parse(sphinx_tree)
            self.sphinxdocs.append(sphinxdoc)

        dox_trees = element.findall("doxydoc")
        for dox_tree in dox_trees:
            doxydoc = DoxyDoc()
            doxydoc.parse(dox_tree)
            self.doxydocs.append(doxydoc)



class QiDocConfig:
    def __init__(self):
        self.repos = list()
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

        repo_trees = element.findall("repo")
        for repo_tree in repo_trees:
            repo = Repo()
            repo.parse(repo_tree)
            self.repos.append(repo)


def parse(config_path):
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
