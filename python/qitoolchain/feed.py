""" Toolchain feeds

"""


import os
import logging
import hashlib
import urllib2
from xml.etree import ElementTree

import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)


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


def handle_package(package, package_tree, toolchain):
    """ Handle a package.

    It is has an url, download and extract it.

    Update the package given as first parameter
    """
    # feed attribue of package_tree is set during parsing
    feed = package_tree.get("feed")
    name = package_tree.get("name")
    if not name:
        raise_parse_error(package_tree, feed, "Missing 'name' attribute")

    package.name = name
    if package_tree.get("url"):
        handle_remote_package(package, package_tree, toolchain)
    if package_tree.get("directory"):
        handle_local_package(package, package_tree)
    if package_tree.get("toolchain_file"):
        handle_toochain_file(package, package_tree)

def handle_remote_package(package, package_tree, toolchain):
    """ Set package.path of the given package,
    downloading it and extracting it if necessary.

    """
    # We use a sha1 for the url to be sure to not downlad the
    # same package twice
    package_url = package_tree.get("url")
    package_name = package_tree.get("name")
    archive_name = hashlib.sha1(package_url).hexdigest()
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

    LOGGER.info("Toolchain %s: adding package %s", toolchain.name, package.name)
    packages_path = qitoolchain.toolchain.get_default_packages_path(toolchain.name)
    should_skip = False
    dest = os.path.join(packages_path, package_name)
    if not os.path.exists(dest):
        should_skip = False
    else:
        dest_mtime = os.stat(dest).st_mtime
        src_mtime  = os.stat(package_archive).st_mtime
        if src_mtime < dest_mtime:
            should_skip = True
    if not should_skip:
        with qibuild.sh.TempDir() as tmp:
            try:
                extracted = qibuild.archive.extract(package_archive, tmp)
            except qibuild.archive.InvalidArchive, err:
                mess = str(err)
                mess += "\nPlease fix the archive and try again"
                raise Exception(mess)
            if os.path.exists(dest):
                qibuild.sh.rm(dest)
            qibuild.sh.mv(extracted, dest)
    package.path = dest


def handle_local_package(package, package_tree):
    """ Set package.path using package.feed

    """
    # feed attribue of package_tree is set during parsing
    feed = package_tree.get("feed")
    directory = package_tree.get("directory")
    feed_root = os.path.dirname(feed)
    package_path = os.path.join(feed_root, directory)
    package_path = qibuild.sh.to_native_path(package_path)
    package.path = package_path


def handle_toochain_file(package, package_tree):
    """ Make sure package.toolchain_file is
    relative to package.path

    """
    toolchain_file = package_tree.get("toolchain_file")
    package_path = package.path
    package.toolchain_file = os.path.join(package_path, toolchain_file)

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
        <select
            arch="linux32"
        />

        """
        self._tree = select_tree

    def select(self, package_tree):
        """ Parse an xml package configuration.
        Returns True if we should keep the
        package

        """
        if self._tree is None:
            return True
        arch = self._tree.get("arch")
        package_arch = package_tree.get("arch")
        if arch:
           if package_arch:
               if package_arch != arch:
                   return False
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
            if self.selector.select(package_tree):
                package_tree.set("feed", feed)
                self.packages.append(package_tree)
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
    package_trees = parser.packages
    for package_tree in package_trees:
        package = qitoolchain.Package(None, None)
        handle_package(package, package_tree, toolchain)
        if package.path is None:
            mess  = "Could not guess package path from configuration\n"
            mess += "Please make sure you have at least an url or a directory\n"
            feed = package_tree.get("feed")
            raise_parse_error(package_tree, feed, mess)
        toolchain.add_package(package)
