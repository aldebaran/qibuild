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
import sys
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
    configstore = qibuild.configstore.ConfigStore()
    cfg_path = get_tc_config_path()
    configstore.read(cfg_path)
    root = configstore.get("default.root")
    if not root:
        root = qibuild.sh.to_native_path("~/.local/share/qi/toolchains")
    res = os.path.join(root, toolchain_name)
    qibuild.sh.mkdir(res, recursive=True)
    return res

def get_tc_cache(toolchain_name):
    """ Return the path where to store packages

    """
    # FIXME: deal with non-UNIX systems
    configstore = qibuild.configstore.ConfigStore()
    cfg_path = get_tc_config_path()
    configstore.read(cfg_path)
    cache = configstore.get("default.cache")
    if not cache:
        cache = qibuild.sh.to_native_path("~/.cache/qi/toolchains")
    res = os.path.join(cache, toolchain_name)
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

    It is able to generate CMake code looking like:
    list(APPEND CMAKE_PREFIX_PATH "~/.local/share/qi/toolchains/linux64/foo")

    It can be initialized with an existing toolchain file.
    In this case, the cmake code will be appended to the toolchain file
    given in the constructor.

    """
    def __init__(self, name):
        self.name = name
        self.configstore = qibuild.configstore.ConfigStore()
        self.configstore.read(get_tc_config_path())
        self.path = get_tc_path(self.name)
        cache = get_tc_cache(name)
        qibuild.sh.mkdir(self.path, recursive=True)
        qibuild.sh.mkdir(cache, recursive=True)
        user_toolchain_file = get_tc_config(self.name, "file")
        if user_toolchain_file:
            if not os.path.exists(user_toolchain_file):
                mess  = "Could not create toolchain named %s\n" % name
                mess += "with toolchain file: '%s'\n" % user_toolchain_file
                mess += "The toolchain file does not exist\n"
                raise Exception(mess)
        self.user_toolchain_file = user_toolchain_file

        self.cmake_flags = get_tc_config(self.name, "cmake.flags", default="").split()
        self.toolchain_file = os.path.join(cache, "toolchain-%s.cmake" % self.name)

        self.packages = list()
        self.load_config()
        self.update_toolchain_file()
        LOGGER.debug("Created a new toolchain:\n%s", str(self))

    def __str__(self):
        res  = "Toolchain %s\n" % self.name
        res += "  path: %s\n" % self.path
        if self.packages:
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
        LOGGER.info("Toolchain %s: adding %s", self.name, name)
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
            with qibuild.sh.TempDir() as tmp:
                try:
                    extracted = qibuild.archive.extract(path, tmp)
                except qibuild.archive.InvalidArchive, err:
                    mess = str(err)
                    mess += "\nPlease fix the archive and try again"
                    raise Exception(mess)
                if os.path.exists(dest):
                    qibuild.sh.rm(dest)
                qibuild.sh.mv(extracted, dest)
        new_package = Package(name)
        matches = [p for p in self.packages if p.name == name]
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
        if self.user_toolchain_file:
            tc_path = qibuild.sh.to_posix_path(self.user_toolchain_file)
            lines = ["include(\"%s\")\n" % tc_path]

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

        # Do not write the file if it's the same
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

    def install_package(self, package_name, destdir, runtime=False):
        """ Install a package to a destdir.

        If a runtime is False, only the runtime files
        (dynamic libraries, executables, config files) will be
        installed

        """
        package_path = self.get(package_name)
        if runtime:
            qibuild.sh.install(package_path, destdir, filter=is_runtime)
        else:
            qibuild.sh.install(package_path, destdir)

    def remove_package(self, package_name):
        """ Remove a package from the toolchain

        """
        package_path = self.get(package_name)
        qibuild.sh.rm(package_path)
        self.packages = [p for p in self.packages if p.name != package_name]
        provides = get_tc_config(self.name, "provides")
        provides = " ".join(p.name for p in self.packages)

        set_tc_config(self.name, "provides", provides)


def is_runtime(filename):
    """ Filter function to only install runtime components of packages

    """
    # FIXME: this looks like a hack.
    # Maybe a user-generated MANIFEST at the root of the package path
    # would be better?

    basename = os.path.basename(filename)
    basedir  = filename.split(os.path.sep)[0]
    if filename.startswith("bin"):
        if sys.platform.startswith("win"):
            if filename.endswith(".exe"):
                return True
            if filename.endswith(".dll"):
                return True
            else:
                return False
        else:
            return True
    if filename.startswith("lib"):
        # exception for python:
        if "python" in filename and filename.endswith("Makefile"):
            return True
        # shared libraries
        shared_lib_ext = ""
        if sys.platform.startswith("win"):
            shared_lib_ext = ".dll"
        if sys.platform == "linux2":
            shared_lib_ext = ".so"
        if sys.platform == "darwing":
            shared_lib_ext = ".dylib"
        if shared_lib_ext in basename:
            return True
        # python
        if basename.endswith(".py"):
            return True
        if basename.endswith(".pyd"):
            return True
        else:
            return False
    if filename.startswith(os.path.join("share", "cmake")):
        return False
    if filename.startswith(os.path.join("share", "man")):
        return False
    if basedir == "share":
        return True
    if basedir == "include":
        # exception for python:
        if filename.endswith("pyconfig.h"):
            return True
        else:
            return False
    if basedir.endswith(".framework"):
        return True

    # True by default: better have too much stuff than
    # not enough
    return True
