## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Toolchain

A set of packages and a toolchain file
"""

import os
import sys
import ConfigParser

import qisys
import qisys.sh
import qibuild.configstore
import qitoolchain
import qitoolchain.feed

from qisys import ui


def get_default_packages_path(tc_name):
    """ Get a default path to store extracted packages

    """
    default_root = qisys.sh.get_share_path("qi", "toolchains")
    config = ConfigParser.ConfigParser()
    cfg_path = get_tc_config_path()
    config.read(cfg_path)
    root = default_root
    if config.has_section("default"):
        try:
            root = config.get("default", "root")
        except ConfigParser.NoOptionError:
            pass
    res = os.path.join(root, tc_name)
    qisys.sh.mkdir(res, recursive=True)
    return res

def get_tc_names():
    """ Return the list of all known toolchains

    They are simply stored in ~/.config/qi/toolchains.cfg
    in this format

        [toolchains]
        linux32=
        linux64=/path/to/linux64/feed.xxml
    """
    config = ConfigParser.ConfigParser()
    config.read(get_tc_config_path())
    if not config.has_section('toolchains'):
        return list()
    tc_items = config.items('toolchains')
    res = [x[0] for x in tc_items]
    res.sort()
    return res

def get_tc_feed(tc_name):
    """ Get the feed associated to a toolchain

    """
    config = ConfigParser.ConfigParser()
    config.read(get_tc_config_path())
    if not config.has_section('toolchains'):
        return None
    return config.get('toolchains', tc_name)


def get_tc_config_path():
    """ Return the general toolchain config file.
    It simply lists all the known toolchains

        [toolchains]
        linux32=
        linux64=
        ...


    """
    return qisys.sh.get_config_path("qi", "toolchains.cfg")


class Package():
    """ A package simply has a name and a path.
    It may also be associated to a toolchain file, relative to its path,
    or a sysroot, also relative to its path

    """
    def __init__(self, name, path, toolchain_file=None, sysroot=None, cross_gdb=None):
        self.name = name
        self.path = path
        self.toolchain_file = toolchain_file
        self.sysroot = None
        self.cross_gdb = None
        if sysroot:
            self.sysroot = os.path.join(self.path, sysroot)
        if cross_gdb:
            self.cross_gdb = os.path.join(self.path, cross_gdb)

        # Quick hack for now
        self.depends = list()

    def install(self, destdir, runtime=True):
        """ Install the package to a destination """
        if runtime:
            qisys.sh.install(self.path, destdir,
                filter_fun=qisys.sh.is_runtime)
        else:
            qisys.sh.install(self.path, destdir)

    def __repr__(self):
        res = "<Package %s in %s"  % (self.name, self.path)
        if self.toolchain_file:
            res += " (using toolchain from %s)" % self.toolchain_file
        if self.sysroot:
            res += "  (sysroot: %s)" % self.sysroot
        if self.cross_gdb:
            res += "  (cross-gdb: %s)" % self.cross_gdb
        res += ">"
        return res

    def __str__(self):
        res = self.name
        res += "\n  in %s" % self.path
        if self.toolchain_file:
            res += "\n  using %s toolchain file" % self.toolchain_file
        if self.sysroot:
            res += "\n  sysroot: " + self.sysroot
        if self.cross_gdb:
            res += "\n  cross-gdb: " + self.cross_gdb
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

class Toolchain(object):
    """ A toolchain is a set of packages

    If has a name that will later be used as 'build config'
    by the BuildWorkTree.

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
        # Stored in general config file when using self.parse_feed,
        # updated by self.load_config()
        self.feed = None
        # Set by self.parse_feed
        self.cmake_generator = None

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
        if self.feed:
            res += "Using feed from %s\n" % self.feed
        else:
            res += "No feed\n"
        if self.packages:
            res += "  Packages:\n"
        else:
            res += "No packages\n"
        # FIXME: the packages should be in the same order as in
        # the feed
        sorted_packages = sorted(self.packages)
        for package in sorted_packages:
            res += " " * 4 + str(package).replace("\n", "\n" + " " * 4)
            res += "\n"
        return res

    def remove(self, force_remove=False):
        """ Remove a toolchain

        Clean cache, remove all packages, remove self from configurations
        """
        qisys.sh.rm(self.cache)

        cfg_path = get_tc_config_path()
        config = ConfigParser.RawConfigParser()
        config.read(cfg_path)
        config.remove_option("toolchains", self.name)
        with open(cfg_path, "w") as fp:
            config.write(fp)

        cfg_path = self._get_config_path()
        qisys.sh.rm(cfg_path)
        if force_remove:
            # With the current design and implementation of qitoolchain, all
            # packages are stored in the following 'tc_path'.
            #
            # This is due to the fact that 'qitoolchain add-package' currently
            # only accept tarballs as input which is extracted under:
            # <tc_path>/<package-name>
            #
            # So, recursively removing 'tc_path' is currently enough to
            # ensure that the whole toolchain, including locally added packages,
            # is removed.
            tc_path = qitoolchain.toolchain.get_default_packages_path(self.name)
            qisys.sh.rm(tc_path)

    def _get_config_path(self):
        """ Returns path to self configuration file

        """
        return qisys.sh.get_config_path("qi", "toolchains", self.name + ".cfg")

    def _get_cache_path(self):
        """ Returns path to self cache directory

        """
        config_path = get_tc_config_path()
        config = ConfigParser.ConfigParser()
        config.read(config_path)
        cache_path = qisys.sh.get_cache_path("qi", "toolchains")
        if config.has_section("default"):
            try:
                root_cfg = config.get("default", "root")
                cache_path = os.path.join(root_cfg, "cache")
            except ConfigParser.NoOptionError:
                pass
        cache_path = os.path.join(cache_path, self.name)
        qisys.sh.mkdir(cache_path, recursive=True)
        return cache_path

    def load_config(self):
        """ Parse configuration, update toolchain file
        when done

        """
        self.feed = get_tc_feed(self.name)
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
                package = Package(package_name, package_path,
                                  toolchain_file=package_conf.get('toolchain_file'),
                                  sysroot=package_conf.get('sysroot'),
                                  cross_gdb=package_conf.get('cross_gdb'))
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
        if package.sysroot:
            qibuild.configstore.update_config(config_path,
            'package "%s"' % package.name,
            "sysroot",
            package.sysroot)
        if package.cross_gdb:
            qibuild.configstore.update_config(config_path,
            'package "%s"' % package.name,
            "cross_gdb",
            package.cross_gdb)
        self.load_config()

    def remove_package(self, name):
        """ Remove a package from the list

        """
        cfg_path = self._get_config_path()
        config = ConfigParser.RawConfigParser()
        config.read(cfg_path)
        package_section = 'package "%s"' % name
        if not config.has_section(package_section):
            mess  = "Could not remove package %s from toolchain %s\n" % (name, self.name)
            mess += "No such package"
            raise Exception(mess)

        tc_path = qitoolchain.toolchain.get_default_packages_path(self.name)
        # Do NOT use self.get here:
        # what we want to remove is the location where the remote package
        # will land, not where it is are right now
        package_path = os.path.join(tc_path, name)
        qisys.sh.rm(package_path)
        config.remove_section(package_section)

        with open(cfg_path, "w") as fp:
            config.write(fp)

        self.load_config()

    def update_toolchain_file(self):
        """ Generates a toolchain file for use by qibuild

        """
        lines = ["# Autogenerated file. Do not edit\n",
                 "# Make sure we don't keep adding elements to this list:\n",
                 "set(CMAKE_FIND_ROOT_PATH "" CACHE INTERNAL "" FORCE)\n",
                 "set(CMAKE_FRAMEWORK_PATH "" CACHE INTERNAL "" FORCE)\n"
        ]

        for package in self.packages:
            if package.toolchain_file:
                tc_file = qisys.sh.to_posix_path(package.toolchain_file)
                lines.append('include("%s")\n' % tc_file)
        for package in self.packages:
            package_path = qisys.sh.to_posix_path(package.path)
            lines.append('list(INSERT CMAKE_FIND_ROOT_PATH 0 "%s")\n' % package_path)
            # For some reason CMAKE_FRAMEWORK_PATH does not follow CMAKE_FIND_ROOT_PATH
            # (well, you seldom use frameworks when cross-compiling ...), so we
            # need to change this variable too
            lines.append('list(INSERT CMAKE_FRAMEWORK_PATH 0 "%s")\n' % package_path)

        oldlines = list()
        if os.path.exists(self.toolchain_file):
            with open(self.toolchain_file, "r") as fp:
                oldlines = fp.readlines()

        # Do not write the file if it's the same
        if lines == oldlines:
            return

        with open(self.toolchain_file, "w") as fp:
            lines = fp.writelines(lines)

    def parse_feed(self, feed, dry_run=False):
        """ Parse an xml feed,
        adding packages to self while doing so

        """
        # Delegate this to qitoolchain.feed module
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read(create_if_missing=True)
        qitoolchain.feed.parse_feed(self, feed, qibuild_cfg, dry_run=dry_run)
        qibuild_cfg.write()

        # Update configuration so we keep which was
        # the last used feed
        self.feed = feed
        config = ConfigParser.ConfigParser()
        config_path = get_tc_config_path()
        config.read(config_path)
        config.set("toolchains", self.name, self.feed)
        with open(config_path, "w") as fp:
            config.write(fp)

    def get(self, package_name, raises=True):
        """ :deprecated: use get_package instead """
        package = self.get_package(package_name, raises=raises)
        if not package:
            return None
        return package.path

    def get_package(self, package_name, raises=True):
        """ Get a package object from the toolchain

        """
        package_names = [p.name for p in self.packages]
        if package_name not in package_names:
            if raises:
                mess  = "Could not get %s from toolchain %s\n" % (package_name, self.name)
                mess += "No such package"
                raise Exception(mess)
            else:
                return None
        package = [p for p in self.packages if p.name == package_name][0]
        return package

    def get_sysroot(self):
        """ Get the sysroot of the toolchain.
        Assume that one and exactly one of the packages inside
        the toolchain has a 'sysroot' attribute

        """
        for package in self.packages:
            if package.sysroot:
                return package.sysroot

    def get_cross_gdb(self):
        """ Get the cross-gdb path from the toolchain.
        Assume that one and exactly one of the packages inside
        the toolchain has a 'cross_gdb' attribute

        """
        for package in self.packages:
            if package.cross_gdb:
                return package.cross_gdb

    def clean_cache(self, dry_run=False):
        tc_cache = self.cache
        dirs_to_rm = os.listdir(tc_cache)
        dirs_to_rm = (os.path.join(tc_cache, x) for x in dirs_to_rm)
        dirs_to_rm = [x for x in dirs_to_rm if os.path.isdir(x)]

        num_dirs = len(dirs_to_rm)
        ui.info(ui.green, "Cleaning cache for", ui.blue, self.name)
        if dry_run:
            ui.info("Would remove %i packages" % num_dirs)
            ui.info("Use -f to proceed")
            return

        for (i, dir_to_rm) in enumerate(dirs_to_rm):
            sys.stdout.write("Removing package %i / %i\r" % ((i + 1), num_dirs))
            sys.stdout.flush()
            qisys.sh.rm(dir_to_rm)
        ui.info(ui.green, "\ndone")

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

