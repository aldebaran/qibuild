## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Toolchain feeds

"""


import os
import urlparse
try:
    # Prefer ElementTree from lxml as it will not reorder attributes when
    # writing XML.
    import lxml.etree as ElementTree
except ImportError:
    from xml.etree import ElementTree

from qisys import ui
import qisys.archive
import qisys.error
import qisys.remote
import qisys.sh
import qisys.version
import qisrc.git
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
    raise qisys.error.Error(mess)

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
                raise qisys.error.Error(
                        "Feed location is not an existing path nor an url")
        tree = ElementTree.ElementTree()
        tree.parse(fp)
    except Exception as e:
        ui.error("Could not parse", feed_location)
        raise qisys.error.Error(str(e))
    finally:
        if fp:
            fp.close()
    return tree

def open_git_feed(toolchain_name, feed_url, name=None, branch="master", first_pass=True):
    git_path = qisys.sh.get_share_path("qi", "toolchains", toolchain_name + ".git")
    git = qisrc.git.Git(git_path)
    if first_pass:
        if os.path.exists(git_path):
            git.call("remote", "set-url", "origin", feed_url)
            git.call("fetch", "origin", "--quiet")
            git.call("reset", "--hard", "--quiet", "origin/%s" % branch)
        else:
            git.clone(feed_url, "--quiet", "--branch", branch)

    feed_rel_path = os.path.join("feeds", name + ".xml")
    feed_path = os.path.join(git_path, feed_rel_path)
    if not os.path.exists(feed_path):
        mess = "No file named %s in %s" % (qisys.sh.to_posix_path(feed_rel_path), feed_url)
        raise qisys.error.Error(mess)
    return feed_path

class ToolchainFeedParser:
    """ A class to handle feed parsing

    """
    def __init__(self, name):
        self.name = name
        self.packages = list()
        self.strict_feed = None
        # A list of packages to be blacklisted
        self.blacklist = list()
        # A dict name -> version used to only keep the latest
        # version
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

    def iter_feeds(self, feed, branch=None, name=None):
        """Recursively parse the feed and yield all the feed paths
        """
        if branch and name:
            feed_path = open_git_feed(self.name, feed, branch=branch, name=name)
        else:
            feed_path = feed

        yield feed_path

        tree = tree_from_feed(feed_path)

        feeds = tree.findall("feed")
        for feed_tree in feeds:
            child = None

            feed_url = feed_tree.get("url")
            if feed_url:
                # feed_url can be relative to feed:
                if not "://" in feed_url:
                    child = urlparse.urljoin(feed, feed_url)
                else:
                    child = feed_url
            else:
                feed_name = feed_tree.get("name")
                if feed_name:
                    child = os.path.join(os.path.dirname(feed_path), feed_name + ".xml")

            if child:
                for i in self.iter_feeds(child):
                    yield i

    def parse(self, feed, branch=None, name=None):
        """ Recursively parse the feed, filling the self.packages

        """

        for feed_path in self.iter_feeds(feed, branch, name):
            tree = tree_from_feed(feed_path)
            root = tree.getroot()
            if self.strict_feed is None:
                self.strict_feed = qisys.qixml.parse_bool_attr(root,
                        "strict_metadata", default=True)

            package_trees = tree.findall("package")
            package_trees.extend(tree.findall("svn_package"))
            for package_tree in package_trees:
                package_tree.set("feed", feed)
                self.append_package(package_tree)

            select_tree = tree.find("select")
            if select_tree is not None:
                blacklist_trees = select_tree.findall("blacklist")
                for blacklist_tree in blacklist_trees:
                    name = blacklist_tree.get("name")
                    if name:
                        self.blacklist.append(name)

    def write_checksums(self, feed):
        for feed_path in self.iter_feeds(feed):
            if not os.access(feed_path, os.W_OK):
                raise qisys.error.Error(
                    "Not a writable file, cannot update checksums: {}".format(feed_path))

            tree = tree_from_feed(feed_path)

            package_trees = tree.findall("package")
            for package_tree in package_trees:
                name_from_feed = package_tree.get("name")
                for package in self.packages:
                    try:
                        name_from_database = package.overriden_properties["name"]
                    except KeyError:
                        name_from_database = package.name

                    if name_from_feed == name_from_database and package.checksum is not None:
                        package_tree.set("checksum", package.checksum)

            tree.write(feed_path)
