""" Toolchain feeds

"""

# FIXME: handle remote stuff

import os
from xml.etree import ElementTree

import qibuild
import qitoolchain

def tree_from_feed(feed_location):
    """ Returns an ElementTree object from an
    feed location

    """
    # FIXME: handle remote feed location
    fp = None
    tree = None
    try:
        fp = open(feed_location, "r")
        tree = ElementTree.ElementTree()
        tree.parse(fp)
    except Exception, e:
        mess  = "Could not parse %s\n" % feed_location
        mess += "Error was: \n"
        mess += str(e)
        raise Exception(mess)
    finally:
        if fp:
            fp.close()
    return tree


def package_from_tree(feed, tree):
    """ Get a package from an XML tree.

    Return None if something is wrong.
    """
    # For error messages:
    as_str = ElementTree.tostring(tree)
    mess  = "Error when parsing feed: '%s'\n" % feed
    mess += "Could not parse:\t%s\n" % as_str

    name = tree.get("name")
    if not name:
        mess += "Missing 'name' attribue"
        raise Exception(mess)
    package_name = name
    package_path = None

    feed_root = os.path.dirname(feed)
    directory = tree.get("directory")
    if directory:
        package_path = os.path.join(feed_root, directory)
        package_path = qibuild.sh.to_native_path(package_path)

    toolchain_path = None
    toolchain_file = tree.get("toolchain_file")
    if toolchain_file:
        toolchain_path = os.path.join(feed_root, toolchain_file)
        toolchain_path = qibuild.sh.to_native_path(toolchain_path)

    return qitoolchain.Package(package_name, package_path, toolchain_path)


def parse_feed(toolchain, feed):
    """ Parse the feed and add the packages in the toolchain

    """
    tree = tree_from_feed(feed)
    package_trees = tree.findall("package")
    for package_tree in package_trees:
        package = package_from_tree(feed, package_tree)
        if package:
            toolchain.add_package(package)

