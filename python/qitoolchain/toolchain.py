##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

import os
import logging
import urllib

import qitools
from qitools.configstore import ConfigStore

LOGGER = logging.getLogger(__name__)


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

        self._projects = list()

    @property
    def projects(self):
        from_conf = self.configstore.get("toolchain", self.name, "provide")
        if from_conf:
            self._projects = from_conf.split()
        else:
            self._projects = list()
        return self._projects

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
        archive_path = os.path.join(get_cache(self.name), package_name)
        if os.path.exists(archive_path):
            # FIXME: do something smarter here...
            pass
        url = self.configstore.get("project", package_name, "url")
        if not url:
            raise Exception("Could not find project %s in feed: %s" % (
                package_name, self.feed))

        LOGGER.debug("Retrieving %s -> %s", url, archive_path)
        urllib.urlretrieve(url, archive_path)
        qitools.archive.extract_tar(archive_path, get_rootfs(self.name))
        self._projects.append(package_name)
        to_write = " ".join(self._projects)
        self._update_config("provide", '"%s"' % to_write)

    def update(self, new_feed=None):
        """Update the toolchain

        """
        if new_feed:
            self.feed = new_feed
        self._update_feed()
        projects = self.configstore.get("project").keys()
        for project in projects:
            self.add_package(project)
        if new_feed:
            self._update_config("feed", new_feed)

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


def create_toolchain(toolchain_name):
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

