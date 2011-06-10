## Copyright (C) 2011 Aldebaran Robotics

""" This package contains the Toolchain and the Package
class

How does it work?

 - Create a Toolchain with a name ("linux" for instance)
    ~/.local/share/qi/toolchains/linux/
and
    ~/.cache/qi/toolchains/linux/packages/
are created.

A toolchain file is created in
~/.local/share/qi/toolchains/linux/toolchain.cmake

qitoolchain build configuration is updated to reflect
there is a toolchain called "linux"

 - Add the foo package:
The foo archive is copied in the cache:
~/.cache/qi/toolchains/linux/packages/foo.tar.gz

The foo package is extraced to the toolchain:
~/.local/share/qi/toolchain/linux/foo/{lib,include,cmake}

The toolchain.cmake in ~/.local/share/qi/toolchains/linux/toolchain.cmake
is updated to contain:

    list(APPEND CMAKE_PREFIX_PATH "~/.local/share/qi/toolchains/linux/foo")

qitoolchain build configuration is updated to
reflect the fact that the "linux" toolchain now provides
the "foo" package.

 - Build a Toc object with the toolchain name "linux", when building a project,
add the -DCMAKE_TOOLCHAIN_FILE parameter

"""


import os
import logging

import qibuild

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
        res = "Package %s"  % self.name
        if self.depends:
            res += " (depends on : %s)" %  " ".join(self.depends)
        return res

    def __lt__(self, other):
        if hasattr(other, 'name'):
            return self.name < other.name
        return self.name < other


def get_tc_config_path():
    """ Return a suitable config path

    """
    # FIXME: deal with non-UNIX systems
    config_path = qibuild.sh.to_native_path("~/.config/qi/toolchain.cfg")
    return config_path

def get_tc_path(toolchain_name):
    """ Return a suitable path to extract the packages

    """
    # FIXME: deal with non-UNIX systems
    res = qibuild.sh.to_native_path("~/.local/share/qi")
    res = os.path.join(res, "toolchains", toolchain_name)
    qibuild.sh.mkdir(res, recursive=True)
    return res

def get_tc_cache(toolchain_name):
    """ Return the path where to store packages

    """
    # FIXME: deal with non-UNIX systems
    cache_path = qibuild.sh.to_native_path("~/.cache/qi")
    res = os.path.join(cache_path, "toolchains", toolchain_name)
    qibuild.sh.mkdir(res, recursive=True)
    return res


def get_toolchain_names():
    """ Return the list of all known toolchains

    """
    config = qibuild.configstore.ConfigStore()
    config.read(get_tc_config_path())
    tc_config = config.get("toolchain")
    if tc_config is None:
        return []
    return tc_config.keys()

def get_tc_config(tc_name, key, default=None):
    """ Get the configuration for a specific toolchain

    """
    configstore = qibuild.configstore.ConfigStore()
    cfg_path = get_tc_config_path()
    configstore.read(cfg_path)
    full_key = 'toolchain.%s.%s' % (tc_name, key)
    return configstore.get(full_key, default=default)

def set_tc_config(tc_name, key, value):
    """ Set the configuration for a specific toolchain

    """
    cfg_path = get_tc_config_path()
    section = 'toolchain "%s"' % tc_name
    qibuild.configstore.update_config(cfg_path, section, key, value)

class Toolchain(object):
    """ The Toolchain class has a name and a list of packages.

    """
    def __init__(self, name):
        self.name = name
        self.configstore = qibuild.configstore.ConfigStore()
        self.configstore.read(get_tc_config_path())
        self.path = get_tc_path(self.name)
        tc_file_from_conf = get_tc_config(self.name, 'file')
        if tc_file_from_conf:
            self.toolchain_file = tc_file_from_conf
        else:
            self.toolchain_file = os.path.join(self.path, "toolchain-%s.cmake" % self.name)

        self.cmake_flags = get_tc_config(self.name, "cmake.flags", default="").split()

        self.packages = list()
        self.cross = get_tc_config(self.name, 'cross')
        if not self.cross:
            self.load_config()
            self.update_toolchain_file()
            LOGGER.debug("Created a new toolchain:\n%s", str(self))

    def __str__(self):
        res  = "Toolchain %s\n" % self.name
        res += "  path: %s\n" % self.path
        if not self.cross:
            res += "  packages:\n" + "\n".join([" " * 4  + x.name for x in sorted(self.packages)])
        return res

    def get(self, package_name):
        """Return path to a package
        """
        known_names = [p.name for p in self.packages]
        if package_name not in known_names:
            raise Exception("No such package: %s" % package_name)
        package_path = os.path.join(self.path, package_name)
        return package_path

    def add_package(self, name, path):
        """Add a package given its name and its path

        """
        # Rename package once it is extracted:
        should_skip = False
        dest = os.path.join(self.path, name)
        if not os.path.exists(dest):
            should_skip = False
        else:
            dest_mtime = os.stat(dest).st_mtime
            src_mtime  = os.stat(path).st_mtime
            if src_mtime < dest_mtime:
                should_skip = True
        if not should_skip:
            LOGGER.info("Extracting package %s", name)
            with qibuild.sh.TempDir() as tmp:
                extracted = qibuild.archive.extract(path, tmp)
                if os.path.exists(dest):
                    qibuild.sh.rm(dest)
                qibuild.sh.mv(extracted, dest)
        new_package = Package(name)
        matches = [p for p in self.packages if p.name == name]
        LOGGER.info("Adding package %s",name)
        if not matches:
            self.packages.append(new_package)
        self.update_tc_provides()
        self.update_toolchain_file()


    def update_tc_provides(self):
        """When a package has been added, update the toolchain
        configuration

        """
        provides = get_tc_config(self.name, "provides")
        provides = " ".join(p.name for p in self.packages)
        LOGGER.debug("update_tc_provides: provides is now %s", provides)
        set_tc_config(self.name, "provides", provides)

    def update_toolchain_file(self):
        """Update the toolchain file when the packages have changed.

        """
        lines = list()
        if self.cmake_flags:
            for flag_setting in self.cmake_flags:
                splitted = flag_setting.split('=')
                if len(splitted) != 2:
                    LOGGER.warning("Ignoring bad cmake flag setting, %s", flag_setting)
                (key, value) = splitted
                lines.append('set(%s "%s" CACHE INTERNAL \"\" FORCE)\n' % (key, value))

        for package in self.packages:
            package_path = self.get(package.name)
            package_path = qibuild.sh.to_posix_path(package_path)
            lines.append('list(APPEND CMAKE_PREFIX_PATH "%s")\n' % package_path)

        oldlines = list()
        try:
            with open(self.toolchain_file, "r") as fp:
                oldlines = fp.readlines()
        except:
            pass
        #do not write the file if it's the same
        if lines == oldlines:
            return
        with open(self.toolchain_file, "w") as fp:
            lines = fp.writelines(lines)


    def load_config(self):
        """ Re-build self.packages list using the configuration file

        Called each time someone uses self.packages
        """
        provides = get_tc_config(self.name, "provides")
        self.packages = list()
        if not provides:
            return
        for package_name in provides.split():
            deps = self.configstore.get("package.%s.depends" % package_name, default="")
            names = deps.split()
            package = Package(package_name)
            package.depends = names
            self.packages.append(package)

def create(toolchain_name):
    """Create a new toolchain given its name.
    """
    path = get_tc_path(toolchain_name)
    qibuild.sh.mkdir(path, recursive=True)
    qibuild.sh.mkdir(get_tc_cache(toolchain_name), recursive=True)
    LOGGER.info("Toolchain initialized in: %s", path)

