## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" Common tools for XML

"""

HAS_LXML = False
from xml.etree import ElementTree as etree

def indent(elem, level=0):
    """ Poor man's pretty print for elementTree

    """
    # Taken from http://infix.se/2007/02/06/gentlemen-indent-your-xml
    i = "\n" + level*"  "
    if len(elem):
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
    """ Parse a boolean attribute of an elelement

      * Return True is the attribute exists and is
        "1" or "true".
      * Returns False if the attribute exist and is
        "0" or "false"
      * If the attribute does not exists and default is given,
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


def write(xml_obj, output):
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
    tree.write(output)


