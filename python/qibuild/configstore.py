## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Nice wrapper around ConfigParser objects.

Highlight: instead of sections and values, the ConfigStore object
uses nested dictionaries.

This enables to store arbitrary depth of configuration "trees".

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
import shlex
import ConfigParser
import qisys.sh

def get_config_dir():
    """ Get a suitable directory to find all the
    config files

    """
    # TODO: handle non-UNIX platforms?
    root = qisys.sh.to_native_path("~/.config/qi")
    qisys.sh.mkdir(root, recursive=True)
    return root

def get_config_path():
    """ Get a writeable global config path

    """
    root = get_config_dir()
    return os.path.join(root, "qibuild.cfg")


class ConfigException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

class ConfigStore:
    """ Store a list of configuration values.

    Values are accessible via dot-separated names.

    Note: there is no set() value, use update_config
    instead.
    """

    def __init__(self):
        self.root = dict()

    def get(self, key, default=None):
        """ Get a value from a dot-separated key

        """
        keys = key.split(".")
        res = ConfigStore._get(self.root, keys)
        if not res:
            return default
        return res


    @staticmethod
    def _get(d, keys):
        """ Recursive function used by self.get().
        Allow sections names to contains at least one dot.

        >>> d = {
        ...     "a"   : {"g" : "h"},
        ...     "n"   : {},
        ... }
        >>> ConfigStore._get(d, 'a.g'.split('.'))
        'h'
        >>> ConfigStore._get(d, 'n'.split('.'))
        {}
        >>> ConfigStore._get(d, 'o'.split('.'))
        """
        k = keys[0]
        rest = keys[1:]
        if not rest:
            return d.get(k)
        if k in d.keys():
            if isinstance(d[k], dict):
                return ConfigStore._get(d[k], rest)
            else:
                return d[k]
        else:
            # Go from ['config', 'linux32-1', '12']
            # to ['config', 'linux32-1.12']
            # FIXME: allow more than one dot?
            k = ".".join(keys[0:2])
            rest = keys[2:]
            if k in d.keys():
                if isinstance(d[k], dict):
                    return ConfigStore._get(d[k], rest)
                else:
                    return d[k]

            return None

    @staticmethod
    def _set(d, keys, value):
        """ Recursive function used by self.read()
        >>> d = {}
        >>> ConfigStore._set(d, "a.b".split("."), "c")
        >>> ConfigStore._set(d, "a.d".split("."), "e")
        >>> d
        {'a': {'b': 'c', 'd': 'e'}}
        >>> d2 = {}
        >>> ConfigStore._set(d2, "a.b.c".split("."), "d")
        >>> ConfigStore._set(d2, "a.b.e".split("."), "f")
        >>> d2
        {'a': {'b': {'c': 'd', 'e': 'f'}}}


        """
        k = keys[0]
        rest = keys[1:]
        if not rest:
            d[k] = value
        else:
            if not d.get(k):
                d[k] = dict()
            ConfigStore._set(d[k], rest, value)


    def __str__(self, pad=True):
        """ print the list of keys/values """
        if not self.root:
            return "None"
        configdict = self.list_child()
        output     = ""

        max_len = 0
        for k in configdict.keys():
            if len(k) > max_len:
                max_len = len(k)
        for k, v in configdict.iteritems():
            if pad:
                pad_space = " " * (max_len - len(k))
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
        parser = ConfigParser.RawConfigParser()
        parser.read(filename)
        parsed_sections = parser.sections()
        for parsed_section in parsed_sections:
            splitted_section = shlex.split(parsed_section)
            # When just parsed, the [config 'bar'] sections have names
            # looking like "config 'bar'", but we really want config.bar
            # as the dot-separated key:
            if len(splitted_section) == 1:
                if self.root.get(parsed_section) is None:
                    self.root[parsed_section] = dict()
                keys = [parsed_section]
            elif len(splitted_section) == 2:
                section_name, subsection = splitted_section
                if self.root.get(section_name) is None:
                    self.root[section_name] = dict()
                self.root[section_name][subsection] = dict()
                keys = [section_name, subsection]

            items = parser.items(parsed_section)
            if not items:
                # The key exists but is empty:
                ConfigStore._set(self.root, keys, dict())
            for k, v in items:
                subkeys = k.split(".")
                subkeys = [x.strip("'") for x in subkeys]
                subkeys = [x.strip("'") for x in subkeys]
                v = v.strip("'")
                v = v.strip('"')
                ConfigStore._set(self.root, keys + subkeys, v)


def update_config(config_path, section, key, value):
    """ Update a config file

    For instance, if foo.cfg is empty,

    After update_config_section(foo.cfg, "bar", "baz", "buzz"):

    foo.cfg looks like:

    [bar]
    baz = buzz

    Note: all comments in the file will be lost!
    Sections will be created if they do not exist.

    Gotcha: this does NOT update a configstore object per se,
    because the configstore may have read several files.

    Here you are just fixing *one* config file, that someone
    else will read later.

    If value is a list, we will write a string separated by spaces

    """
    parser = ConfigParser.ConfigParser()
    parser.read(config_path)
    if not parser.has_section(section):
        parser.add_section(section)
    if type(value) == type(""):
        parser.set(section, key, value)
    if type(value) == type([""]):
        parser.set(section, key, " ".join(value))
    qisys.sh.mkdir(os.path.dirname(config_path), recursive=True)
    with open(config_path, "w") as config_file:
        parser.write(config_file)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
