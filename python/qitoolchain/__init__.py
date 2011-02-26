## Copyright (C) 2011 Aldebaran Robotics

""" This package contains the Toolchain and the Package
class

How does it work?

 - Create a Toolchain with a name ("linux" for instance)
/path/to/share/qi/toolchains/rootfs/linux
and
/path/to/share/qi/toolchains/cache/linux
are created.
qitoolchain build configuration is updated to reflect
there is a toolchain called "linux"

 - Add the foo package:
The foo archive is extracted in:
/path/to/share/qi/toolchains/rootfs/<name>/foo
qitoolchain build configuration is update to
reflect the fact that the "linux" toolchain now provides
the "foo" package.

 - Build a Toc object with the toolchain name "linux",
When finding a project depending on foo, add the foo package
path to the list of SDK dirs to use

"""


import os
import sys
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
    """ Return a suitable config path"""
    # FIXME: deal with non-UNIX systems
    config_path = os.path.expanduser("~/.config/qi/toolchain.cfg")
    return config_path

def get_shared_path():
    """ Return a suitable path to put toolchain files """
    if sys.platform.startswith("win"):
        # > Vista:
        if os.environ.get("LOCALAPPDATA"):
            res = os.path.expandvars(r"%LOCALAPPDATA%\qi")
        else:
            res = os.path.expandvars(r"%APPDATA%\qi")
    else:
        res = os.path.expanduser("~/.local/share/qi")

    qitools.sh.mkdir(res, recursive=True)
    return res

def get_rootfs(toolchain_name):
    """ Return a suitable path to extract the packages

    """
    res = os.path.join(get_shared_path(), "toolchains", "rootfs",
            toolchain_name)
    qitools.sh.mkdir(res, recursive=True)
    return res

def get_cache(toolchain_name):
    res = os.path.join(get_shared_path(), "toolchains", "cache",
            toolchain_name)
    qitools.sh.mkdir(res, recursive=True)
    return res


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
        self._load_feed_config()
        self._packages = list()

    def __str__(self):
        ret = ""
        ret += "feed     = %s\n" % self.feed
        ret += "packages = %s" % ",".join([ str(x) for x in self.packages])
        return ret

    @property
    def packages(self):
        """List of packages in this toolchain.

        This list is always up to date.
        """
        self._load_feed_config()
        return self._packages

    def get(self, package_name):
        """Return path to a package """
        base_dir = get_rootfs(self.name)
        package_path = os.path.join(base_dir, package_name)
        return package_path

    def add_local_package(self, package_path):
        """Add a package given its name and its path

        """
        package_name = os.path.basename(package_path)
        package_name = package_name.split(".")[0]
        qitools.archive.extract(package_path, get_rootfs(self.name))
        self._update_tc_provides(package_name)


    def add_remote_package(self, package_name):
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
        self._add_package(package_name)
        self._update_tc_provides(package_name)

    def _update_tc_provides(self, package_name):
        """When a package has been added, update the tooclchain
        configuration

        """
        provided = self.configstore.get("toolchain", self.name, "provide",
            default="").split()
        LOGGER.debug("[%s] toolchain: new package %s providing %s",
                          self.name,
                          package_name,
                          ",".join(provided))
        if package_name not in provided:
            provided.append(package_name)
            to_write = " ".join(provided)
            self._update_config("provide", '"%s"' % to_write)

    def _add_package(self, package_name):
        """Add just one package. Called by self.add_package
        which does resolve dependencies.

        """
        # FIXME: recurse until every dependency is handled, here the
        # dependencies may also have dependencies themselves...
        archive_path = os.path.join(get_cache(self.name), package_name)
        if sys.platform.startswith("win"):
            archive_path += ".zip"
        else:
            archive_path += ".tar.gz"
        if os.path.exists(archive_path):
            # FIXME: do something smarter here...
            pass
        url = self.configstore.get("package", package_name, "url")
        if not url:
            raise Exception("Could not find package %s in feed: %s" % (
                package_name, self.feed))

        LOGGER.info("Adding package %s", package_name)
        urllib.urlretrieve(url, archive_path)
        qitools.archive.extract(archive_path, get_rootfs(self.name))
        self._packages.append(Package(package_name))

    def update(self, new_feed=None, all=False):
        """Update the toolchain

        """
        if new_feed:
            self.feed = new_feed
        self._update_feed()
        if all:
            package_names = self.configstore.get("package", default=dict()).keys()
        else:
            package_names = [p.name for p in self.packages]
        for package_name in package_names:
            self.add_remote_package(package_name)
        if new_feed:
            self._update_config("feed", new_feed)

    def _load_feed_config(self):
        """ Re-build self._packages list using the configuration file

        Called each time someone uses self.packages
        """
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

        self.configstore.read(self.config_path)

    def _update_feed(self):
        """Update the feed configuration file"""
        feed_path = os.path.join(get_cache(self.name), "feed.cfg")
        if not self.feed:
            return
        urllib.urlretrieve(self.feed, feed_path)
        self.configstore.read(feed_path)


def create(toolchain_name):
    """Create a new toolchain given its name.
    """
    rootfs = get_rootfs(toolchain_name)
    LOGGER.info("Toolchain initialized in: %s", rootfs)

