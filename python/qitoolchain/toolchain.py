##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

import os
import posixpath
import logging

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


    def download(self, package):
        """Retrieve the latest version from the server, if not already
        in cache

        Then, extract the package to the toolchains subdir
        """
        cache = get_cache(self.name)
        remote_subdir = posixpath.join("toolchains", self.name)
        archive_name_regexp = package
        # FIXME: use self.feed instead
        with qitools.ftp.FtpConnection("ananas") as ftp:
            res = ftp.download(remote_subdir, [archive_name_regexp], output_dir=cache)

        if len(res) != 1:
            LOGGER.error("Expecting exactly one result, got: %s", res)
            return

        base_dir = get_rootfs(self.name)
        qitools.archive.extract_tar(res[0], base_dir)


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

