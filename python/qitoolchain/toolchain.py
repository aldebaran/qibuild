""" Toolchain

A set of packages and a toolchain file
"""

import os
import ConfigParser

import qibuild
import qitoolchain

CONFIG_PATH = "~/.config/qi/"
CACHE_PATH  = "~/.cache/qi"
SHARE_PATH  = "~/.local/share/qi/"


def get_default_packages_path(tc_name):
    """ Get a default path to store extracted packages

    """
    configstore = qibuild.configstore.ConfigStore()
    cfg_path = get_tc_config_path()
    configstore.read(cfg_path)
    root = configstore.get("default.root")
    if not root:
        root = qibuild.sh.to_native_path(SHARE_PATH)
        root = os.path.join(SHARE_PATH, "toolchains")
    res = os.path.join(root, tc_name)
    qibuild.sh.mkdir(res, recursive=True)
    return res

def get_tc_names():
    """ Return the list of all known toolchains

    They are simply stored in ~/.config/qi/toolchains.cfg
    in this format

        [toolchains]
        linux32=
        linu64=
    """
    config = ConfigParser.ConfigParser()
    config.read(get_tc_config_path())
    if not config.has_section('toolchains'):
        return list()
    tc_items = config.items('toolchains')
    return [x[0] for x in tc_items]

def get_tc_config_path():
    """ Return the general toolchain config file.
    It simply lists all the known toolchains

        [toolchains]
        linux32=
        linux64=
        ...


    """
    config_path = qibuild.sh.to_native_path(CONFIG_PATH)
    qibuild.sh.mkdir(CONFIG_PATH, recursive=True)
    config_path = os.path.join(config_path, "toolchains.cfg")
    return config_path


class Package():
    """ A package simply has a name and a path.
    It may also be associated to a toolchain file, relative to its path

    """
    def __init__(self, name, path, toolchain_file=None):
        self.name = name
        self.path = path
        self.toolchain_file = None
        if toolchain_file:
            toolchain_file = os.path.join(self.path, toolchain_file)
            self.toolchain_file = toolchain_file
        # Quick hack for now
        self.depends = list()

    def __repr__(self):
        res = "<Package %s in %s"  % (self.name, self.path)
        if self.toolchain_file:
            res += " (using toolchain from %s)" % self.toolchain_file
        res += ">"
        return res

    def __str__(self):
        res = self.name
        res += "\nIn %s" % self.path
        if self.toolchain_file:
            res += "\nUsing %s toolchain file" % self.toolchain_file
        return res

    def __eq__(self, other):
        if self.name  != other.name:
            return False
        if self.path != other.path:
            return False
        if self.toolchain_file != self.toolchain_file:
            return False
        return True

    def __lt__(self, other):
        return self.name < other.name

class Toolchain:
    """ A toolchain is a set of packages

    It has a configuration in ~/.config/qi/toolchains/<name.cfg>
    looking like:

      [package foo]
      path = '~/.cache/share/qi/ .... '
      toolchain_file = '...'

      [package naoqi-sdk]
      path = 'path/to/naoqi-sdk'

    thus added packages are stored permanentely.

    """
    def __init__(self, name):
        self.name = name
        self.packages = list()
        self.cache = self._get_cache_path()
        self.toolchain_file  = os.path.join(self.cache, "toolchain-%s.cmake" % self.name)

        # Add self to the list of known toolchains:
        if not self.name in get_tc_names():
            config = ConfigParser.ConfigParser()
            config_path = get_tc_config_path()
            config.read(config_path)
            if not config.has_section("toolchains"):
                config.add_section("toolchains")
            config.set("toolchains", self.name, "")
            with open(config_path, "w") as fp:
                config.write(fp)

        self.cmake_flags = list()
        self.load_config()

    def __str__(self):
        res  = "Toolchain %s\n" % self.name
        if self.packages:
            res += "  Packages:\n"
        for package in self.packages:
            res += " " * 4 + str(package).replace("\n", "\n" + " " * 4)
        return res


    def remove(self):
        """ Remove a toolchain

        Clean cache, remove all packages, remove self from configurations
        """
        qibuild.sh.rm(self.cache)

        cfg_path = get_tc_config_path()
        tc_section = 'toolchain "%s"' % self.name

        config = ConfigParser.RawConfigParser()
        config.read(cfg_path)

        config.remove_section(tc_section)
        with open(cfg_path, "w") as fp:
            config.write(fp)


    def _get_config_path(self):
        """ Returns path to self configuration file

        """
        config_path = qibuild.sh.to_native_path(CONFIG_PATH)
        config_path = os.path.join(config_path, "toolchains")
        qibuild.sh.mkdir(config_path, recursive=True)
        config_path = os.path.join(config_path, self.name + ".cfg")
        return config_path

    def _get_cache_path(self):
        """ Returns path to self cache directory

        """
        cache_path = qibuild.sh.to_native_path(CACHE_PATH)
        cache_path = os.path.join(cache_path, "toolchains", self.name)
        qibuild.sh.mkdir(cache_path, recursive=True)
        return cache_path



    def load_config(self):
        """ Parse configuration, update toolchain file
        when done

        """
        config_path = self._get_config_path()
        configstore = qibuild.configstore.ConfigStore()
        configstore.read(config_path)
        packages_conf = configstore.get('package')
        self.packages = list()
        if packages_conf:
            for (package_name, package_conf) in packages_conf.iteritems():
                package_path = package_conf.get('path')
                if not package_path:
                    mess  = "Invalid configuration for toolchain %s\n" % self.name
                    mess += "(from '%s')\n" % config_path
                    mess += "Package %s has no 'path' setting" % package_name
                    raise Exception(mess)
                package_tc_file = package_conf.get('toolchain_file')
                package = Package(package_name, package_path, package_tc_file)
                self.packages.append(package)

        self.update_toolchain_file()


    def add_package(self, package):
        """ Add a package to the list

        """
        config_path = self._get_config_path()
        qibuild.configstore.update_config(config_path,
            'package "%s"' % package.name,
            "path",
            package.path)
        if package.toolchain_file:
            qibuild.configstore.update_config(config_path,
            'package "%s"' % package.name,
            "toolchain_file",
            package.toolchain_file)
        self.load_config()

    def remove_package(self, name):
        """ Remove a package from the list

        """
        cfg_path = self._get_config_path()
        config = ConfigParser.RawConfigParser()
        config.read(cfg_path)
        package_section = 'package "%s"' % name
        if not config.has_section(package_section):
            mess  = "Could not remove %s from toolchain %s\n" % (self.name, name)
            mess += "No such package"
            raise Exception(mess)
        config.remove_section(package_section)

        with open(cfg_path, "w") as fp:
            config.write(fp)

        self.load_config()


    def update_toolchain_file(self):
        """ Generates a toolchain file for use by qibuild

        """
        lines = ["# Autogenerated file. Do not edit\n"]

        for package in self.packages:
            package_path = qibuild.sh.to_posix_path(package.path)
            lines.append("# %s\n" % package.name)
            if package.toolchain_file:
                tc_file = qibuild.sh.to_posix_path(package.toolchain_file)
                lines.append('include("%s")\n' % tc_file)
            lines.append('list(APPEND CMAKE_PREFIX_PATH "%s")\n' % package_path)

        oldlines = list()
        try:
            with open(self.toolchain_file, "r") as fp:
                oldlines = fp.readlines()
        except:
            pass

        # Do not write the file if it's the same
        if lines == oldlines:
            return

        with open(self.toolchain_file, "w") as fp:
            lines = fp.writelines(lines)


    def parse_feed(self, feed):
        """ Recursively parse an xml feed,
        adding packages to the feed while doing so

        """
        qitoolchain.feed.parse_feed(self, feed)

    def get(self, package_name):
        """ Get the path to a package

        """
        package_names = [p.name for p in self.packages]
        if package_name not in package_names:
            mess  = "Could not install %s from toolchain %s" % (package_name, self.name)
            mess += "No such package"
            raise Exception(mess)
        package = [p for p in self.packages if p.name == package_name][0]
        package_path = package.path
        return package_path


    def install_package(self, package_name, destdir, runtime=False):
        """ Install a package to a destdir.

        If a runtime is False, only the runtime files
        (dynamic libraries, executables, config files) will be
        installed

        """
        package_path = self.get(package_name)
        if runtime:
            qibuild.sh.install(package_path, destdir, filter=qibuild.sh.is_runtime)
        else:
            qibuild.sh.install(package_path, destdir)

