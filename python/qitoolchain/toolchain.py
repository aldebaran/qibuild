##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

import os
import posixpath
import logging
import urllib

import qitools
import qitoolchain
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
        base_dir = qitoolchain.get_rootfs(self.name)
        package_path = os.path.join(base_dir, package_name)
        return package_path

    def update_feed(self):
        """Update the feed configuration file"""
        LOGGER.debug("updating feed: %s", self.feed)
        feed_path = os.path.join(get_cache(self.name), "feed.cfg")
        urllib.urlretrieve(self.feed, feed_path)
        self.configstore.read(feed_path)
        LOGGER.debug("config is now: %s", self.configstore)

    def download(self, package_name):
        """Retrieve the latest version from the server, if not already
        in cache

        Then, extract the package to the toolchains subdir
        """
        self.update_feed()
        archive_path = os.path.join(get_cache(self.name), package_name)
        if os.path.exists(archive_path):
            return
        url = self.configstore.get("project", package_name, "url")
        if not url:
            raise Exception("Could not find project %s in feed: %s" %
                package_name, self.feed)

        urllib.urlretrieve(url, archive_path)
        base_dir = os.path.join(get_rootfs(self.name), package_name)
        qitools.archive.extract_tar(archive_path, base_dir)


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

