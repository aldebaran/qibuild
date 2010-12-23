##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

""" store all toc configuration keys
"""

import os
import logging
import ConfigParser

def read(filename, configstore, prefix=""):
    """ read a configuration file """
    parser = ConfigParser.RawConfigParser()
    parser.read(filename)
    sections = parser.sections()
    for section in sections:
        splitted_section = section.split()
        items = parser.items(section)
        for k, v in items:
            tkey = [ ]
            if prefix:
                tkey.append(prefix)
            tkey.extend([x.strip("\"\'") for x in splitted_section])
            tkey.extend([x.strip("\"\'") for x in k.split(".")])
            configstore.add(tkey, v.strip("\"\'"))


class ConfigStore:
    """
    store a list of config of the form:
    titi.toto.tata = paf
    toc.tac.tic = pof
    """
    logger = logging.getLogger("qibuild.configstore")

    def __init__(self):
        self.root = dict()

    @classmethod
    def _add_key(cls, element, key):
        """ add a key """
        t = element.get(key, None)
        if t is None:
            element[key] = dict()
            t = element[key]
        elif type(t) != dict:
            raise Exception("The key is a leaf")
        return t

    def add(self, names, value):
        """
        add a value
        names is a list, the full name is names0.names1...namesn
        """
        elem = self.root
        for n in names[:-1]:
            elem = self._add_key(elem, n)
        elem[names[len(names) - 1]] = value

    def get(self, *args):
        """
        """
        element = self.root
        for s in args:
            if not isinstance(element, dict):
                raise TocException("Could not find %s in %s" % (s, root_element))
            element = element.get(s, None)
            if element is None:
                return None
        return element

    def __str__(self, element = None, name = ""):
        """ print the list of keys/values """
        output = ""
        if element is None:
            element = self.root
        if len(name) > 0:
            name = name + '.'
        for (k, v) in element.items():
            if type(v) == dict:
                output += self.__str__(v, name + k)
            else:
                output += "%s%s = %s\n" % (name, k, str(v))
        return output

    def recurse(self, callback, element = None, name = ""):
        """ print the list of keys/values """
        if element is None:
            element = self.root
        if len(name) > 0:
            name = name + '.'
        for (k, v) in element.items():
            if type(v) == dict:
                self.recurse(callback, v, name + k)
            else:
                callback(str(name+k), str(v))

    def list_child(self, element = None, name = ""):
        """
        return a dict with k = value
        """
        ret = dict()
        if element is None:
            element = self.root
        if len(name) > 0:
            name = name + '.'
        for (k, v) in element.items():
            if type(v) == dict:
                r = self.list_child(v, name + k)
                ret.update(r)
            else:
                ret[name + k] = v
        return ret



