## Copyright (C) 2011 Aldebaran Robotics

"""Add a package to a feed

The feed should be a local file.
"""

import logging
from xml.etree import ElementTree

import qibuild

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
    parser.add_argument("feed_path", metavar='FEED',
        help="The path to the feed")
    parser.add_argument("package_name", metavar='PACKAGE_NAME',
        help="The name of the package")
    parser.add_argument("package_url", metavar='PACKAGE_URL',
        help="The path to the package")
    parser.add_argument("--arch",
        help="The arch of the package")
    parser.add_argument("--version",
        help="The version of the package")


def do(args):
    """ Main entry point

    """
    arch    = args.arch
    version = args.version
    package_name = args.package_name
    package_url  = args.package_url
    feed_path    = args.feed_path

    feed_path = qibuild.sh.to_native_path(feed_path)

    tree = ElementTree.ElementTree()
    try:
        with open(feed_path, "r") as fp:
            tree.parse(fp)
    except Exception, e:
        mess  = "Could not parse feed '%s'\n" % feed_path
        mess += "Error was: \n"
        mess += str(e)
        raise Exception(mess)


    known_package_trees = tree.findall("package")
    for known_package_tree in known_package_trees:
        known_url = known_package_tree.get("url")
        if known_url == package_url:
            mess  = "Could not add package %s to feed %s\n" % (package_name, feed_path)
            mess += "There is already a package with the same URL ('%s'):\n" % known_url
            mess += "\t" + ElementTree.tostring(known_package_tree)
            raise Exception(mess)

    package_tree = ElementTree.Element("package")
    package_tree.set("name", package_name)
    package_tree.set("url",  package_url)

    if arch:
        package_tree.set("arch", arch)

    if version:
        package_tree.set("version", version)

    root = tree.getroot()
    root.insert(0, package_tree)

    with open(feed_path, "w") as fp:
        tree.write(fp)


