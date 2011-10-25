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

    package_url = tree.get("url")
    if package_url:
        return package_from_url(toolchain, package_url, package_name)

    return None


def package_from_archive(toolchain, package_name, archive_path):
    """ Extract an archive in the cache, then
    return a qitoolchain.Package object

    """
    packages_path = qitoolchain.toolchain.get_default_packages_path(toolchain.name)
    should_skip = False
    dest = os.path.join(packages_path, package_name)
    res = qitoolchain.Package(package_name, dest)
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
    return res

def package_from_url(toolchain, package_url, package_name):
    """ Get a package from an url

    """
    # We use a sha1 for the url to be sure to not downlad the
    # same package twice
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
    return package_from_archive(toolchain, package_name, package_archive)

def parse_feed(toolchain, feed):
    """ Parse the feed and add the packages in the toolchain

    """
    tree = tree_from_feed(feed)
    package_trees = tree.findall("package")
    for package_tree in package_trees:
        package = package_from_tree(toolchain, feed, package_tree)
        if package:
            toolchain.add_package(package)
    feeds = tree.findall("feed")
    for feed_tree in feeds:
        feed_url = feed_tree.get("url")
        if feed_url:
            parse_feed(toolchain, feed_url)

