## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
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
import qisys.remote
import qisys.version
import qibuild
import qitoolchain



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
            fp = qisys.remote.open_remote_location(feed_location)
        tree = ElementTree.ElementTree()
        tree.parse(fp)
    except Exception:
        ui.error("Could not parse", feed_location)
        raise
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
        handle_remote_package(feed, package, package_tree, toolchain)
    if package_tree.get("directory"):
        handle_local_package(package, package_tree)
    if package_tree.get("toolchain_file"):
        handle_toochain_file(package, package_tree)
    package.cross_gdb = package_tree.get("cross_gdb")
    package.sysroot = package_tree.get("sysroot")
    cmake_generator = package_tree.get("cmake_generator")
    if cmake_generator:
        toolchain.cmake_generator = cmake_generator

def handle_remote_package(feed, package, package_tree, toolchain):
    """ Set package.path of the given package,
    downloading it and extracting it if necessary.

    """
    package_url = package_tree.get("url")
    package_name = package_tree.get("name")

    if "://"  in feed:
        # package_url may be relative to the feed url:
        package_url = urlparse.urljoin(feed, package_url)

    # We use a sha1 for the url to be sure to not downlad the
    # same package twice
    # pylint: disable-msg=E1101
    archive_name = hashlib.sha1(package_url).hexdigest()
    top = archive_name[:2]
    rest = archive_name[2:]
    extension = package_url.rsplit(".", 1)[1]
    if package_url.endswith(".tar." + extension):
        rest += ".tar"
    rest += "." + extension
    output = toolchain.cache
    output = os.path.join(output, top)
    message = (ui.green, "Downloading", ui.blue, package_url)
    package_archive = qisys.remote.download(package_url,
        output,
        output_name=rest,
        clobber=False,
        message=message)

    ui.info(ui.green, "Adding package", ui.blue, package.name)
    packages_path = qitoolchain.toolchain.get_default_packages_path(toolchain.name)
    should_skip = False
    dest = os.path.join(packages_path, package_name)
    dest = os.path.abspath(dest)
    if not os.path.exists(dest):
        should_skip = False
    else:
        dest_mtime = os.stat(dest).st_mtime
        src_mtime  = os.stat(package_archive).st_mtime
        if src_mtime < dest_mtime:
            should_skip = True
    if not should_skip:
        if os.path.exists(dest):
            qisys.sh.rm(dest)
        try:
            algo = qisys.archive.guess_algo(package_archive)
            extract_path = qisys.archive.extract(package_archive, packages_path, algo=algo)
            extract_path = os.path.abspath(extract_path)
            if extract_path != dest:
                src = extract_path
                dst = dest
                qisys.sh.mkdir(dst, recursive=True)
                qisys.sh.rm(dst)
                qisys.sh.mv(src, dst)
                qisys.sh.rm(src)
        except qisys.archive.InvalidArchive, err:
            mess = str(err)
            mess += "\nPlease fix the archive and try again"
            raise Exception(mess)
    package.path = dest


def handle_local_package(package, package_tree):
    """ Set package.path using package.feed

    """
    # feed attribue of package_tree is set during parsing
    feed = package_tree.get("feed")
    directory = package_tree.get("directory")
    feed_root = os.path.dirname(feed)
    package_path = os.path.join(feed_root, directory)
    package_path = qisys.sh.to_native_path(package_path)
    package.path = package_path


def handle_toochain_file(package, package_tree):
    """ Make sure package.toolchain_file is
    relative to package.path

    """
    toolchain_file = package_tree.get("toolchain_file")
    package_path = package.path
    # toolchain_file can be an url too
    if not "://" in toolchain_file:
        package.toolchain_file = os.path.join(package_path, toolchain_file)
    else:
        tc_file = qisys.remote.download(toolchain_file, package_path)
        package.toolchain_file = tc_file

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
        res = [x for x in self.packages if not x.get("name") in self.blacklist]
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
            self.packages.append(package_tree)
        else:
            if version is None:
                # if version not defined, don't keep it
                return
            prev_version = self._versions[name]
            if qisys.version.compare(prev_version, version) > 0:
                return
            else:
                self.packages = [x for x in self.packages if x.get("name") != name]
                self.packages.append(package_tree)
                self._versions[name] = version

    def parse(self, feed):
        """ Recursively parse the feed, filling the self.packages

        """
        tree = tree_from_feed(feed)
        package_trees = tree.findall("package")
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


def parse_feed(toolchain, feed, qibuild_cfg, dry_run=False):
    """ Helper for toolchain.parse_feed

    """
    # Reset toolchain.packages:
    package_names = [package.name for package in toolchain.packages]
    for package_name in package_names:
        toolchain.remove_package(package_name)
    parser = ToolchainFeedParser()
    parser.parse(feed)
    package_trees = parser.get_packages()
    errors = list()
    for package_tree in package_trees:
        package = qitoolchain.Package(None, None)
        if dry_run:
            package_name = package_tree.get("name")
            package_url  = package_tree.get("url")
            # Check that url can be opened
            fp = None
            try:
                fp = qisys.remote.open_remote_location(package_url)
            except Exception, e:
                error = "Could not add %s from %s\n" % (package_name, package_url)
                error += "Error was: %s" % e
                errors.append(error)
                continue
            finally:
                if fp:
                    fp.close()
            if package_url:
                print "Would add ", package_name, "from", package_url
            continue
        else:
            handle_package(package, package_tree, toolchain)
        if package.path is None:
            mess  = "could guess package path from this configuration:\n"
            mess += ElementTree.tostring(package_tree)
            mess += "Please make sure you have at least an url or a directory\n"
            ui.warning(mess)
            continue
        if not dry_run:
            toolchain.add_package(package)

    if dry_run and errors:
        print "Errors when parsing %s\n" % feed
        for error in errors:
            print error
        sys.exit(2)

    # Finally, if the feed contains a cmake_generator,
    # add it to the qibuild config
    if toolchain.cmake_generator:
        config = qibuild.config.Config()
        config.name = toolchain.name
        config.cmake.generator = toolchain.cmake_generator
        qibuild_cfg.add_config(config)
        qibuild_cfg.write()
