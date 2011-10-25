""" Toolchain feeds

"""


import os
import hashlib
import urllib2
from xml.etree import ElementTree

import qibuild
import qitoolchain


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
            fp = urllib2.urlopen(feed_location)
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


def package_from_tree(toolchain, feed, tree):
    """ Get a package from an XML tree.

    Return None if something is wrong.
    """
    # For error messages:
    as_str = ElementTree.tostring(tree)
    mess  = "Error when parsing feed: '%s'\n" % feed
    mess += "Could not parse:\t%s\n" % as_str

    package.feed = feed
    name = tree.get("name")
    if not name:
        mess += "Missing 'name' attribue"
        raise Exception(mess)

    package.url = tree.get("url")
    package.arch = tree.get("arch")
    package.version = tree.get("version")
    package.directory = tree.get("directory")
    package.toolchain_file = tree.get("toolchain_file")

    return None

def handle_package(toolchain, package):
    """ Handle a package.

    It is has an url, download and extract it.
    """
    if package.url:
        handle_remote_package(toolchain, package)
    if package.directory:
        handle_local_package(package)
    if package.toolchain_file:
        handle_toochain_file(package)

def handle_remote_package(toolchain, package):
    """ Set package.path of the given package,
    downloading it and extracting it if necessary.

    """
    # We use a sha1 for the url to be sure to not downlad the
    # same package twice
    archive_name = hashlib.sha1(package.url).hexdigest()
    top = archive_name[:2]
    rest = archive_name[2:]
    if package_url.endswith(".tar.gz"):
        rest += ".tar.gz"
    if package_url.endswith(".zip"):
        rest += ".zip"
    output = toolchain.cache
    output = os.path.join(output, top)
    message = "Getting package %s from %s" % (package_name, package_url)
    package_archive = qitoolchain.remote.download(package_url,
        output,
        output_name=rest,
        clobber=False,
        message=message)

    packages_path = qitoolchain.toolchain.get_default_packages_path(toolchain.name)
    should_skip = False
    dest = os.path.join(packages_path, package_name)
    if not os.path.exists(dest):
        should_skip = False
    else:
        dest_mtime = os.stat(dest).st_mtime
        src_mtime  = os.stat(archive_path).st_mtime
        if src_mtime < dest_mtime:
            should_skip = True
    if not should_skip:
        with qibuild.sh.TempDir() as tmp:
            try:
                extracted = qibuild.archive.extract(archive_path, tmp)
            except qibuild.archive.InvalidArchive, err:
                mess = str(err)
                mess += "\nPlease fix the archive and try again"
                raise Exception(mess)
            if os.path.exists(dest):
                qibuild.sh.rm(dest)
            qibuild.sh.mv(extracted, dest)
    package.path = dest


def handle_local_package(toolchain, package):
    """ Set package.path using package.feed

    """
    feed = package.feed
    feed_root = os.path.dirname(feed)
    package.path = os.path.join(feed_root, package.directory)


def handle_toochain_file(package):
    """ Make sure package.toolchain_file is
    relative to package.path

    """
    package.toolchain_file = os.path.join(package.path, package.toolchain_file)

class PackageSelector:
    """ A class to handle package selection

    Usage:
        selector = PackageSelector()
        selector.parse(tree) # where tree in a select xml configuration
        selector.select(package)

    """
    def __init__(self):
        self._tree = None

    def parse(self, select_tree):
        """ Read an xml configuration looking like
        <select>
            <arch>linux32</arch>
        </select>

        """
        self._tree = select_tree

    def select(self, package_tree):
        """ Parse an xml package configuration.
        Returns True if we should keep the
        package

        """
        if self._tree is None:
            return True
        return True


class ToolchainFeedParser:
    """ A class to handle feed parsing

    """
    def __init__(self, toolchain):
        self.toolchain = toolchain
        self.packages = list()
        self.selector = PackageSelector()


    def parse(self, feed):
        """ Recursively parse the feed, filling the packages
        last variable

        """
        tree = tree_from_feed(feed)
        select_tree = tree.find("select")
        if select_tree is not None:
            self.selector.parse(select_tree)
        package_trees = tree.findall("package")
        for package_tree in package_trees:
            package = package_from_tree(self.toolchain, feed, package_tree)
            if package:
                if self.selector.select(package):
                    self.packages.append(package)
        feeds = tree.findall("feed")
        for feed_tree in feeds:
            feed_url = feed_tree.get("url")
            if feed_url:
                self.parse(feed_url)


def parse_feed(toolchain, feed):
    """ Recursively parse an xml feed,
    adding packages to the feed while doing so

    """
    parser = ToolchainFeedParser(toolchain)
    parser.parse(feed)
    packages = parser.packages
    for package in packages:
        handle_package(package)
        toolchain.add_package(package)
