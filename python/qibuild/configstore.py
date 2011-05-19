## Copyright (C) 2011 Aldebaran Robotics

""" Nice wrapper around ConfigParser objects.

Highlight: instead of sections and values, the ConfigStore object
uses nested dictionaries.

This enables to store abritrary depth of configuration "trees".

For instance, with

foo.cfg looking like

    [project "foo"]
    bar.baz = 42
    bar.spam = "eggs"

[project "bar"]

You can use:

    conf = ConfigStore()
    conf.read("foo.cfg")

    projects = conf.get("project")

    # Project is now a dictionary

    # Returns 42
    projects["foo"]["bar"]

"""

import os
import logging
import ConfigParser

import qibuild

class ConfigException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

class ConfigStore:
    """ Store a list of configuration values
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

    def list_child(self, element = None, name = ""):
        """
        return a dict with k = value
        """
        ret = dict()
        if element is None:
            element = self.root
        if len(name) > 0:
            name = name + '.'
        if not element.items():
            ret[name[:-1]] = ""
        for (k, v) in element.items():
            if type(v) == dict:
                r = self.list_child(v, name + k)
                ret.update(r)
            else:
                ret[name + k] = v
        return ret

    def read(self, filename):
        """ read a configuration file """
        self.logger.debug("loading: %s", filename)
        parser = ConfigParser.RawConfigParser()
        parser.read(filename)
        sections = parser.sections()
        for section in sections:
            splitted_section = section.split()
            items = parser.items(section)
            if not items:
                self.set(*splitted_section, value=dict())
            for k, v in items:
                tkey = [ ]
                tkey.extend([x.strip("\"\'") for x in splitted_section])
                tkey.extend([x.strip("\"\'") for x in k.split(".")])
                self.set(*tkey, value=v.strip("\"\'"))


def update_config(config_path, section, name, key, value):
    """Update a config file.

    For instance, if foo.cfg looks like

    [spam "eggs"]
    answer = 42

    after update_config(foo.cfg, "spam", "eggs", "anser", 43):

    foo.cfg looks like

    [spam "eggs"]
    anser = 43

    Note: all comments in the file will be lost!
    Sections will be created if they do not exist.

    Gotcha: this does NOT update a configstore object per se,
    because the configstore may have read several files.

    Here you are just fixing *one* config file, that someone
    else will read later.

    """
    parser = ConfigParser.ConfigParser()
    parser.read(config_path)
    section_name = '%s "%s"' % (section, name)
    if not parser.has_section(section_name):
        parser.add_section(section_name)
    if type(value) == type(""):
        parser.set(section_name, key, value)
    if type(value) == type([""]):
        parser.set(section_name, key, " ".join(value))
    qibuild.sh.mkdir(os.path.dirname(config_path), recursive=True)
    with open(config_path, "w") as config_file:
        parser.write(config_file)

