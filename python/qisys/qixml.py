## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" This is just a set of convenience functions to be used with
`The ElemtTree XML API <http://docs.python.org/library/xml.etree.elementtree.html>`_

"""

import re
from qisys import ui

from xml.etree import ElementTree as etree

def indent(elem, level=0):
    """ Poor man's pretty print for elementTree

    """
    # Taken from http://infix.se/2007/02/06/gentlemen-indent-your-xml
    i = "\n" + level*"  "
    if len(elem):  # Can't use "if elem": etree advises against it for future compat
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def raise_parse_error(message, xml_path=None, tree=None):
    """ Raise a nice parsing error about the given
    tree element

    """
    mess = ""
    if xml_path:
        mess += "Error when parsing '%s'\n" % xml_path
    if tree is not None:
        as_str = etree.tostring(tree)
        mess += "Could not parse:\t%s\n" % as_str
    mess += message
    raise Exception(mess)

def parse_bool_attr(tree, name, default=False):
    """ Parse a boolean attribute of an element

      * Return True is the attribute exists and is
        "1" or "true".
      * Returns False if the attribute exist and is
        "0" or "false"
      * If the attribute does not exist and default is given,
        returns `default`
      * Otherwise raise an exception

    """
    res = tree.get(name)
    if res in ["true", "1"]:
        return True
    if res in ["false", "0"]:
        return False
    if res is not None:
        raise_parse_error("Expecting value in [true, false, 0, 1] "
            "for attribute %s" % name,
            tree=tree)
    return default

def parse_int_attr(tree, name, default=None):
    """ Parse a integer from a xml element

    """
    res = tree.get(name)
    if not res:
        if default is None:
            mess = "node %s must have a '%s' attribute" % (tree.tag, name)
            raise_parse_error(mess, tree=tree)
        else:
            return default
    try:
        res = int(res)
    except ValueError:
        mess = "Could not parse attribue '%s' from node %s \n" % (name, tree.tag)
        mess += "Excepting an integer, got: %s" % res
        raise_parse_error(mess, tree=tree)
    return res


def parse_list_attr(tree, name):
    """ Parse a list attribute
    Return an empty list if the attribute is not found

    """
    res = tree.get(name, "")
    return res.split()


def parse_required_attr(tree, name, xml_path=None):
    """ Raise an exception if an attribute it missing in a
    Node
    """
    value = tree.get(name)
    if not value:
        mess = "node %s must have a '%s' attribute" % (tree.tag, name)
        raise_parse_error(mess, xml_path=xml_path)
    return value



def read(xml_path):
    """ Return a etree object from an xml path

    """
    tree = etree.ElementTree()
    try:
        tree.parse(xml_path)
    except Exception, e:
        raise_parse_error(str(e), xml_path=xml_path)
    return tree


def write(xml_obj, output, **kwargs):
    """ Write an xml object to the given path

    If xml_obj is not an ElementTree but an
    Element,  we will build a tree just to write it.

    The result of the writing will always be nicely
    indented
    """
    tree = None
    root = None
    if isinstance(xml_obj, etree.ElementTree):
        tree = xml_obj
        root = xml_obj.getroot()
    else:
        tree = etree.ElementTree(element=xml_obj)
        root = xml_obj
    indent(root)
    tree.write(output, **kwargs)


class XMLParser(object):
    """ This class provides an easy interface to parse XML tags element by element.
    To work with it, you must inherit from this class and define methods on tags
    you want to parse.

    """

    def __init__(self, target):
        """ Initialize the XMLParser with a root element.

        :param root: The root element.

        """
        self.target = target
        self._root = None
        self._ignore = list()
        self._required = list()
        self.backtrace = list()

    def parse(self, root):
        """ This function iterates on the children of the element (or the root if an
        element is not given) and call ``_parse_TAGNAME`` functions.

        :param root: The root element that should be parsed.

        """
        self._root = root
        self._parse_prologue()
        self._parse_attributes()
        self.backtrace.append(root.tag)
        for child in root:
            method_name = "_parse_{tagname}".format(tagname = child.tag)
            try:
                method = getattr(self.__class__, method_name)
            except AttributeError as err:
                self._parse_unknown_element(child, err)
                continue
            if method.func_code.co_argcount != 2:
                mess = "Handler for tag `%s' must take" % child.tag
                mess += " two arguments. (method: %s, takes " % method_name
                mess += "%d argument(s))" % method.func_code.co_argcount
                raise TypeError(mess)
            method(self, child)
        self.backtrace.pop()
        self._parse_epilogue()

    def _parse_unknown_element(self, element, err):
        """ This function will by default ignore unknown elements. You can overload
        it to change its behavior.

        :param element: The unknown element.
        :param err: The error message.

        """
        pass

    def _parse_prologue(self):
        """ You can overload this function to do something before the beginning of
        parsing of the file.

        """
        pass

    def _parse_epilogue(self):
        """ You can overload this function to do something after the end of the
        parsing of the file.

        """
        pass

    def _parse_attributes(self):
        """ You can overload this function to get attribute of root before parsing
        its children. Attributes will be a dictionary.

        """
        apply_xml_attributes(self.target, self._root, ignore_list=self._ignore)
        for name in self._required:
            self.check_needed(name)
        self._post_parse_attributes()

    def _post_parse_attributes(self):
        """ You can overload this function to add post treatment to parsing of
        attributes. Attributes will be a dictionary.

        """
        pass

    def check_needed(self, attribute_name, node_name=None, value=None):
        if node_name is None:
            node_name = self.target.__class__.__name__.lower()

        if value is None:
            if hasattr(self.target, attribute_name):
                value = getattr(self.target, attribute_name)

        if value is None:
            mess = "Node '%s' must have a '%s' attribute" % (node_name,
                                                               attribute_name)
            raise Exception(mess)

    def xml_elem(self, node_name=None):
        """ Get the xml representation of the target

        Will set attributes of the node using attributes of the target,
        except if _dump_<attribute> class exits

        """
        if not node_name:
            node_name = self.target.__class__.__name__.lower()
        res = etree.Element(node_name)

        def is_public(name):
            return not name.startswith("_")

        def is_serializable(value):
            # no way to guess that from etree api:
            return type(value) in (list, bool, str, unicode, int)

        target_dir = dir(self.target)
        for member in target_dir:
            if not is_public(member):
                continue
            if member in self._ignore:
                continue
            method = None
            method_name = "_write_%s" % member
            try:
                method = getattr(self, method_name)
            except AttributeError:
                pass
            if method:
                if method.func_code.co_argcount != 2:
                    mess = "Handler for member `%s' must take" % member
                    mess += " two arguments. (method: %s, takes " % method_name
                    mess += "%d argument(s))" % method.func_code.co_argcount
                    raise TypeError(mess)
                method(res)
                continue
            member_value = getattr(self.target, member)
            if is_serializable(member_value):
                if type(member_value) == bool:
                    if member_value:
                        res.set(member, "true")
                    else:
                        res.set(member, "false")
                elif type(member_value) == list:
                    if member_value:
                        res.set(member, " ".join(member_value))
                else:
                    res.set(member, str(member_value))
        return res


def apply_xml_attributes(target, elem, ignore_list=None):
    """ For each attribute of the xml element,
    set the attribute in the target if this one
    already exists, while matching the type

    """
    if not ignore_list:
        ignore_list = list()
    for attr in elem.attrib:
        if attr in ignore_list:
            continue
        if hasattr(target, attr):
            default_value = getattr(target, attr)
            type_value = type(default_value)
            new_value = _get_value_for_type(type_value, elem.attrib[attr])
            try:
                setattr(target, attr, new_value)
            except AttributeError:
                ui.warning("Could not set", attr, "on", target, "with value",
                            new_value)


def _get_value_for_type(type_value, value):
    if type_value == bool:
        if value.lower() in ["true", "1"]:
            return True
        if value.lower() in ["false", "0"]:
            return False
        mess = "Waiting for a boolean but value is '%s'." % value
        raise Exception(mess)
    if type_value == list:
        return value.split(" ")
    return value

def sanitize_xml(val, replacement="?"):
    """  Remove illegal XML characters from the input string.
    Useful when trying to write raw strings from unknow location
    to an XML file ::

        as_bytes = open("wtf.txt").read()
        as_bytes = qisys.qixml.remove_control_chars(bytes)
        as_unicode = bytes.decode(errors="ignore")

        # ...
        element.text = as_unicode

        tree.write(fp, encoding=...)

    """
    # taken from http://lsimons.wordpress.com/2011/03/17/stripping-illegal-characters-out-of-xml-in-python/
    # unicode invalid characters
    _illegal_xml_chars_RE = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')
    return _illegal_xml_chars_RE.sub(replacement, val)
