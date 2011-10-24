""" Toolchain

A set of packages and a toolchain file



"""

CONFIG_PATH = "~/.config/qi/"
CACHE_PATH  = "~/.cache/qi"

import ConfigParser

import os
import qibuild

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
    """ A package simply has a name and a path

    """
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __repr__(self):
        res = "<Package %s in %s>"  % (self.name, self.path)
        return res


    def __eq__(self, other):
        return self.name == other.name and self.path == other.path

    def __lt__(self, other):
        return self.name < other.name

class Toolchain:
    """ A toolchain is a set of packages

    It has a configuration in ~/.config/qi/toolchains/<name.cfg>
    looking like:

      [toolchain 'name']
      arch = <arch>

      # Additional CMake flags required to use this toolchain
      # (for instance CMAKE_OSX_ARCHITECTURES on mac)
      # cmake.flags =
      # Custom toolchain file to be used when using this toolchain
      # (for instanche when cross-compiling)
      # toolchain_file = '/path/to/ctc/toolchain-atom.cmake'

      [package foo]
      path = '~/.cache/share/qi/ .... '

      [package naoqi-sdk]
      path = 'path/to/naoqi-sdk'

    thus added packages are stored permanentely.

    """
    def __init__(self, name):
        self.name = name
        self.packages = list()
        cache_path = self._get_cache_path()
        self.toolchain_file  = os.path.join(cache_path, "toolchain-%s.cmake" % self.name)

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

        self.user_toolchain_file = None
        self.cmake_flags = list()

        self.load_config()


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
                package = Package(package_name, package_path)
                self.packages.append(package)

        tc_file = configstore.get("toolchain.toolchain_file")
        if tc_file:
            self.user_toolchain_file = tc_file

        cmake_flags_cfg = configstore.get("toolchain.cmake.flags")
        if cmake_flags_cfg:
            flag_settings = cmake_flags_cfg.split()
            for flag_setting in flag_settings:
                splitted = flag_setting.split('=')
                if len(splitted) != 2:
                    mess  = "Invalid cmake.flags setting for toolchain %s\n" % self.name
                    mess += "(%s)\n" % cmake_flags_cfg
                    mess += "cmake.flags should be a space separated list of KEY=VALUE\n"
                    raise Exception(mess)
                (key, value) = splitted
                self.cmake_flags.append((key, value))
        else:
            self.cmake_flags = list()

        self.update_toolchain_file()


    def add_package(self, package):
        """ Add a package to the list

        """
        config_path = self._get_config_path()
        qibuild.configstore.update_config(config_path,
            'package "%s"' % package.name,
            "path",
            package.path)
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
        """

        """
        # Read [(path, name)] from self.packages,
        # Generate text
        #    # Autogenerated by qibuild. Do not edit
        #    list(APPEND CMAKE_PREFIX_PATH ...."
        lines = ["# Autogenerated file. Do not edit\n"]
        if self.user_toolchain_file:
            tc_path = qibuild.sh.to_posix_path(self.user_toolchain_file)
            lines.append("include(\"%s\")\n" % tc_path)

        for (key, value) in self.cmake_flags:
            lines.append('set(%s "%s" CACHE INTERNAL \"\" FORCE)\n' % (key, value))

        for package in self.packages:
            package_path = qibuild.sh.to_posix_path(package.path)
            lines.append("# %s\n" % package.name)
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



def tc_handle_feed(toolchain, feed_location, tree):
    feeds = tree.findall("feed")
    for feed in feeds:
        # Get the url attrib
        # feed_location = ...
        tc_handle_feed(toolchain, feed_location)

    packages = tree.findall("package")
    for package in packages:
        tc_handle_package(toolchain, feed_location, package)



def tc_handle_package(toolchain, feed_location, package):
    pass
    # check 'arch' attrib and toolchain.arch

    # handle 'url' attrib of package:
    # sha1(url) -> extract in ~/.local/share/qi/toolchain/<SHA1>
    # using mtime so that it works

    # handle 'directory' attrib of package
    # concat feed_location base dir in package directory
    # (handle feed_location being a url of a path)

    # Create Package object, add it to the toolchain
