##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010, 2011 Aldebaran Robotics
##

""" store all toc configuration keys
"""

import os
import logging
import ConfigParser

class ConfigException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

class ConfigStore:
    """
    store a list of config of the form:
    titi.toto.tata = paf
    toc.tac.tic = pof
    """
    logger = logging.getLogger("qibuild.configstore")

    def __init__(self):
        self.root = dict()

    def set(self, *keys, **kargs):
        """
        add a value
        names is a list, the full name is names0.names1...namesn
        """
        value = kargs['value']
        element = self.root

        for key in keys[:-1]:
            current = element.get(key, None)
            if current is None:
                element[key] = dict()
                current      = element[key]
            elif type(current) != dict:
                raise ConfigException("The key is a leaf")
            element = current
        element[keys[len(keys) - 1]] = value

    def get(self, *args, **kargs):
        """
        """
        default = kargs.get('default')
        element = self.root
        for s in args:
            if not isinstance(element, dict):
                raise ConfigException("Could not find %s in %s" % (s, self.root))
            element = element.get(s, None)
            if element is None:
                return default
        return element

    def __str__(self, pad=True):
        """ print the list of keys/values """
        configdict = self.list_child()
        output     = ""

        max_len = 0
        for k in configdict.keys():
            if len(k) > max_len:
                max_len = len(k)
        for k,v in configdict.iteritems():
            if pad:
                pad_space = "".join([ " " for x in range(max_len - len(k)) ])
            else:
                pad_space = ""
            output += "  %s%s = %s\n" % (k, pad_space, str(v))
        if output.endswith("\n"):
            output = output[:-1]
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



    def read(self, filename, prefix=""):
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
                self.set(*tkey, value=v.strip("\"\'"))
