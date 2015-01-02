## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Toolchain feeds

"""


import os
import sys
import hashlib
import urlparse
from xml.etree import ElementTree

from qisys import ui
import qisys
import qisys.archive
import qisys.remote
import qisys.version
import qibuild.config
import qitoolchain


def is_url(location):
    """ Check that a given location is an URL """
    return "://" in location


def raise_parse_error(package_tree, feed, message):
    """ Raise a nice pasing error about the given
    package_tree element.

    """
    as_str = ElementTree.tostring(package_tree)
    mess  = "Error when parsing feed: '%s'\n" % feed
    mess += "Could not parse:\t%s\n" % as_str
    mess += message
    raise Exception(mess)


def tree_from_feed(feed_location):
    """ Returns an ElementTree object from an
    feed location

    """
    fp = None
    tree = None
    try:
        if os.path.exists(feed_location):
            fp = open(feed_location, "r")
        else:
            if is_url(feed_location):
                fp = qisys.remote.open_remote_location(feed_location)
            else:
                raise Exception("Feed location is not an existing path nor an url")
        tree = ElementTree.ElementTree()
        tree.parse(fp)
    except Exception:
        ui.error("Could not parse", feed_location)
        raise
    finally:
        if fp:
            fp.close()
    return tree


class ToolchainFeedParser:
    """ A class to handle feed parsing

    """
    def __init__(self):
        self.packages = list()
        # A dict name -> version used to only keep the latest
        # version
        self.blacklist = list()
        self._versions = dict()

    def get_packages(self):
        """ Get the parsed packages """
        res = [x for x in self.packages if not x.name in self.blacklist]
        return res

    def append_package(self, package_tree):
        """ Add a package to self.packages.
        If an older version of the package exists,
        replace by the new version

        """
        version = package_tree.get("version")
        name = package_tree.get("name")

        names = self._versions.keys()
        if name not in names:
            self._versions[name] = version
            self.packages.append(qitoolchain.qipackage.from_xml(package_tree))
        else:
            if version is None:
                # if version not defined, don't keep it
                return
            prev_version = self._versions[name]
            if prev_version and qisys.version.compare(prev_version, version) > 0:
                return
            else:
                self.packages = [x for x in self.packages if x.name != name]
                self.packages.append(qitoolchain.qipackage.from_xml(package_tree))
                self._versions[name] = version

    def parse(self, feed):
        """ Recursively parse the feed, filling the self.packages

        """
        tree = tree_from_feed(feed)
        package_trees = tree.findall("package")
        package_trees.extend(tree.findall("svn_package"))
        for package_tree in package_trees:
            package_tree.set("feed", feed)
            self.append_package(package_tree)
        feeds = tree.findall("feed")
        for feed_tree in feeds:
            feed_url = feed_tree.get("url")
            if feed_url:
                # feed_url can be relative to feed:
                if not "://" in feed_url:
                    feed_url = urlparse.urljoin(feed, feed_url)
                self.parse(feed_url)
        select_tree = tree.find("select")
        if select_tree is not None:
            blacklist_trees = select_tree.findall("blacklist")
            for blacklist_tree in blacklist_trees:
                name = blacklist_tree.get("name")
                if name:
                    self.blacklist.append(name)
