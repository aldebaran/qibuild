##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

"""This package contains the
Toolchain class and the qitoolchain actions

"""


import os
import logging
import urllib

import qitools
from qitools.configstore import ConfigStore

LOGGER = logging.getLogger(__name__)


class Package:
    """A package is a set of binaries, headers and cmake files
    (a bit like a -dev debian package)
    It has a name and may depend on other packages.

    """
    def __init__(self, name):
        self.name = name
        self.depends = list()

    def __str__(self):
        res = "Package %s\n"  % self.name
        res += "depends on : %s" %  " ".join(self.depends)
        return res


def get_config_path():
    """Returns a suitable config path"""
    # FIXME: deal with non-UNIX systems
    config_path = os.path.expanduser("~/.config/qi/toolchain.cfg")
    return config_path

def get_shared_path():
    # FIXME: deal with non-UNIX systems
    share_path = os.path.expanduser("~/.local/share/qi")
    return share_path

def get_rootfs(toolchain_name):
    return os.path.join(get_shared_path(), "toolchains", "rootfs",
            toolchain_name)

def get_cache(toolchain_name):
    return os.path.join(get_shared_path(), "toolchains", "cache",
            toolchain_name)


class Toolchain(object):
    """The Toolchain class has a name and a list of packages.


    """
    def __init__(self, name):
        if name == None:
            self.name = "system"
        else:
            self.name = name
        self.feed = None
        self.config_path = get_config_path()
        self.shared_path = get_shared_path()
        self.configstore = ConfigStore()
        self.configstore.read(get_config_path())
        self.feed = self.configstore.get("toolchain", self.name, "feed")
        self.cache = get_cache(self.name)
        self.rootfs = get_rootfs(self.name)

        # Set self._packages with correct dependencies
        self._update_feed()
        self._load_feed_config()
        self._packages = list()

    @property
    def packages(self):
        self._load_feed_config()
        return self._packages

    def get(self, package_name):
        """Return path to a package """
        base_dir = get_rootfs(self.name)
        package_path = os.path.join(base_dir, package_name)
        return package_path

    def add_package(self, package_name):
        """Retrieve the latest version from the server, if not already
        in cache

        Then, extract the package to the toolchains subdir.

        Finally, update toolchain.provide settings
        """
        self._update_feed()
        deps = self.configstore.get("package", package_name, "depends",
            default="").split()
        for dep in deps:
            self._add_package(dep)

        provided = self.configstore.get("toolchain", self.name, "provide",
            default="").split()
        if package_name not in provided:
            provided.append(package_name)
            to_write = " ".join(provided)
            self._update_config("provide", '"%s"' % to_write)

    def _add_package(self, package_name):
        """Add just one package. called by self.add_package
        which does resolved dependencies.

        (in a non-recursive way because I'm bored)

        """
        archive_path = os.path.join(get_cache(self.name), package_name)
        if os.path.exists(archive_path):
            # FIXME: do something smarter here...
            pass
        url = self.configstore.get("package", package_name, "url")
        if not url:
            raise Exception("Could not find package %s in feed: %s" % (
                package_name, self.feed))

        LOGGER.debug("Retrieving %s -> %s", url, archive_path)
        urllib.urlretrieve(url, archive_path)
        qitools.archive.extract_tar(archive_path, get_rootfs(self.name))
        self._packages.append(Package(package_name))

    def update(self, new_feed=None, all=False):
        """Update the toolchain

        """
        if new_feed:
            self.feed = new_feed
        self._update_feed()
        if all:
            package_names = self.configstore.get("package").keys()
        else:
            package_names = [p.name for p in self.packages]
        for package_name in package_names:
            self.add_package(package_name)
        if new_feed:
            self._update_config("feed", new_feed)

    def _load_feed_config(self):
        provided = self.configstore.get("toolchain", self.name, "provide")
        self._packages = list()
        if not provided:
            return
        for package_name in provided.split():
            deps = self.configstore.get("package", package_name, "depends",
                default="")
            names = deps.split()
            package = Package(package_name)
            package.depends = names
            self._packages.append(package)

        LOGGER.debug("Loaded feed config\n" +
            "\n".join([str(p) for p in self._packages]))

    def _update_config(self, name, value):
        """Update the toolchain configuration file

        """
        LOGGER.debug("updating config %s : %s", name, value)
        import ConfigParser
        parser = ConfigParser.ConfigParser()
        parser.read(self.config_path)

        toolchain_section = 'toolchain "%s"' % self.name
        if parser.has_section(toolchain_section):
            parser.set(toolchain_section, name, value)

        with open(self.config_path, "w") as config_file:
            parser.write(config_file)


    def _update_feed(self):
        """Update the feed configuration file"""
        feed_path = os.path.join(get_cache(self.name), "feed.cfg")
        urllib.urlretrieve(self.feed, feed_path)
        self.configstore.read(feed_path)


def create(toolchain_name):
    """Create a new toolchain given its name.
    """
    rootfs = get_rootfs(toolchain_name)
    if os.path.exists(rootfs):
        raise Exception("Toolchain '%s' already exists." % toolchain_name)
    qitools.sh.mkdir(rootfs, recursive=True)
    cache = get_cache(toolchain_name)
    if not os.path.exists(cache):
        qitools.sh.mkdir(cache,  recursive=True)
    LOGGER.info("Toolchain initialized in: %s", rootfs)

