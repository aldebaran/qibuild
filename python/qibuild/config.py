## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" Read / write qibuild configuration file

"""

import os
import operator
import locale

from qisys import ui

import qisys.qixml
import qisys.sh
from qisys.qixml import etree



def get_global_cfg_path():
    """ Get path to global config file

    """
    return qisys.sh.get_config_path("qi", "qibuild.xml")


class Env(object):
    def __init__(self):
        self.path = None
        self.bat_file = None
        self.editor = None
        self.vars = dict()

    def parse(self, tree):
        self.path = tree.get("path")
        self.bat_file = tree.get("bat_file")
        self.editor   = tree.get("editor")
        self.parse_vars(tree)

    def tree(self):
        tree = etree.Element("env")
        if self.path:
            tree.set("path", self.path)
        if self.bat_file:
            tree.set("bat_file", self.bat_file)
        if self.editor:
            tree.set("editor", self.editor)
        self.dump_vars(tree)
        return tree

    def parse_vars(self, tree):
        var_elems = tree.findall("var")
        for var_elem in var_elems:
            name = qisys.qixml.parse_required_attr(var_elem, "name")
            self.vars[name] = var_elem.text

    def dump_vars(self, tree):
        for name, value in self.vars.iteritems():
            var_elem = etree.SubElement(tree, "var")
            var_elem.set("name", name)
            var_elem.text = value

    def __str__(self):
        res = ""
        if self.path:
            res += "env.path: %s\n" % self.path
        if self.bat_file:
            res += "env.bat_file: %s\n" % self.bat_file
        if self.editor:
            res += "env.editor: %s\n" % self.editor
        if self.vars:
            res += "env.vars: %s\n" % self.vars
        return res


class IDE(object):
    def __init__(self):
        self.name = None
        self.path = None

    def parse(self, tree):
        name = tree.get("name")
        if not name:
            qisys.qixml.raise_parse_error("ide node should have a name attribute",
                tree=tree)
        self.name = name
        self.path = tree.get("path")

    def tree(self):
        tree = etree.Element("ide")
        tree.set("name", self.name)
        if self.path:
            tree.set("path", self.path)
        return tree

    def __str__(self):
        res = self.name
        res += "\n"
        if self.path:
            res += "  path: %s\n" % self.path
        return res


class CMake(object):
    def __init__(self):
        self.generator = None

    def parse(self, tree):
        self.generator = tree.get("generator")

    def tree(self):
        tree = etree.Element("cmake")
        if self.generator:
            tree.set("generator", self.generator)
        return tree

    def __str__(self):
        res = ""
        if self.generator:
            res += "cmake.generator: %s\n" % self.generator
        return res


class Defaults(object):
    def __init__(self):
        # An editor name to use by default
        self.editor = None
        # An ide name to use by default
        self.ide = None
        # A cmake config to use by default (for intance, a CMake generator)
        self.cmake = CMake()
        # An env config to use by default
        self.env = Env()

    def parse(self, tree):
        env_tree = tree.find("env")
        if env_tree is not None:
            self.env.parse(env_tree)
        cmake_tree = tree.find("cmake")
        if cmake_tree is not None:
            self.cmake.parse(cmake_tree)
        self.ide = tree.get("ide")

    def tree(self):
        tree = etree.Element("defaults")
        if self.ide:
            tree.set("ide", self.ide)
        env_tree = self.env.tree()
        tree.append(env_tree)
        cmake_tree = self.cmake.tree()
        tree.append(cmake_tree)
        return tree

    def __str__(self):
        res = ""
        if self.ide:
            res += "  defaults.ide: %s\n" % self.ide
        cmake_str = str(self.cmake)
        if cmake_str:
            res += ui.indent(cmake_str) + "\n"
        env_str = str(self.env)
        if env_str:
            res += ui.indent(env_str) + "\n"
        return res


class Access(object):
    def __init__(self):
        self.root = None
        self.username = None
        self.password = None

    def parse(self, tree):
        self.root = tree.get("root")
        self.username = tree.get("username")
        self.password = tree.get("password")

    def tree(self):
        tree = etree.Element("access")
        if self.root:
            tree.set("root", self.root)
        if self.username:
            tree.set("username", self.username)
        if self.password:
            tree.set("password", self.password)
        return tree

    def __str__(self):
        res = ""
        if self.username:
            res += "username: %s\n" % self.username
        if self.password:
            res += "password: XXXXX\n"
        return res


class Server(object):
    def __init__(self):
        self.name = None
        self.access = Access()

    def parse(self, tree):
        name = tree.get("name")
        if not name:
            qisys.qixml.raise_parse_error("server node should have a name attribute",
                tree=tree)
        self.name = name
        access_tree = tree.find("access")
        if access_tree is not None:
            self.access.parse(access_tree)

    def tree(self):
        tree = etree.Element("server")
        if self.name:
            tree.set("name", self.name)
        access_tree = self.access.tree()
        tree.append(access_tree)
        return tree

    def __str__(self):
        res = self.name
        access_str = str(self.access)
        if access_str:
            res += "\n"
            res += ui.indent(access_str)
        return res

class WorkTree(object):
    def __init__(self):
        self.path = None
        self.defaults = LocalDefaults()

    def parse(self, tree):
        path = tree.get("path")
        if not path:
            qisys.qixml.raise_parse_error(
                    "'worktree' node should have a 'path' attribute")
        self.path = path
        defaults_tree = tree.find("defaults")
        if defaults_tree is not None:
            self.defaults.parse(defaults_tree)

    def tree(self):
        tree = etree.Element("worktree")
        tree.set("path", self.path)
        tree.append(self.defaults.tree())
        return tree

    def __str__(self):
        encoding = locale.getpreferredencoding()
        as_bytes = self.path.encode(encoding)
        res = "worktree in %s" % as_bytes
        defaults_str = str(self.defaults)
        if defaults_str:
            res += "\n  " + defaults_str
        return res

class LocalSettings(object):
    def __init__(self):
        self.defaults = LocalDefaults()
        self.build = LocalBuild()

    def parse(self, tree):
        defaults_tree = tree.find("defaults")
        if defaults_tree is not None:
            self.defaults.parse(defaults_tree)
        build_tree = tree.find("build")
        if build_tree is not None:
            self.build.parse(build_tree)

    def tree(self):
        tree = etree.Element("qibuild")
        tree.set("version", "1")
        tree.append(self.defaults.tree())
        tree.append(self.build.tree())
        return tree

    def __str__(self):
        res = ""
        defaults_str = str(self.defaults)
        if defaults_str:
            res += "default settings for this worktree:\n"
            res += ui.indent(defaults_str) + "\n"
        build_str = str(self.build)
        if build_str:
            res += "build settings for this worktree:\n"
            res += ui.indent(build_str) + "\n"
        return res


class LocalDefaults(object):
    def __init__(self):
        # An config name to use by default
        self.config = None

    def parse(self, tree):
        self.config = tree.get("config")

    def tree(self):
        tree = etree.Element("defaults")
        if self.config:
            tree.set("config", self.config)
        return tree

    def __str__(self):
        res = ""
        if self.config:
            res += "default config: %s\n" % self.config
        return res

class LocalBuild(object):
    def __init__(self):
        self.sdk_dir = None
        self.prefix = None

    def parse(self, tree):
        # Not calling to_native_path because build_dir and sdk_dir can be
        # relative to the worktree
        self.prefix = tree.get("prefix")
        self.sdk_dir = tree.get("sdk_dir")

    def tree(self):
        tree = etree.Element("build")
        if self.prefix:
            tree.set("prefix", self.prefix)
        if self.sdk_dir:
            tree.set("sdk_dir", self.sdk_dir)
        return tree

    def __str__(self):
        res = ""
        if self.prefix:
            res += "build prefix: %s\n" % self.prefix
        if self.sdk_dir:
            res += "sdk_dir: %s\n" % self.sdk_dir
        return res


class BuildConfig(object):
    def __init__(self):
        self.name = None
        # The name of an ide
        self.ide = None
        self.env = Env()
        self.cmake = CMake()
        self.toolchain = None
        self.profiles = list()
        self.host = False

    def parse(self, tree):
        name = tree.get("name")
        if not name:
            qisys.qixml.raise_parse_error("'config' node must have a 'name' attribute",
                tree=tree)
        self.name = ui.valid_filename(name)
        self.ide = tree.get("ide")
        env_tree = tree.find("env")
        self.host = qisys.qixml.parse_bool_attr(tree, "host")
        if env_tree is not None:
            self.env.parse(env_tree)
        cmake_tree = tree.find("cmake")
        if cmake_tree is not None:
            self.cmake.parse(cmake_tree)
        toolchain_elem = tree.find("toolchain")
        if toolchain_elem is not None:
            self.toolchain = toolchain_elem.text
        profiles_tree = tree.find("profiles")
        if profiles_tree is not None:
            profile_elems = profiles_tree.findall("profile")
            for profile_elem in profile_elems:
                self.profiles.append(profile_elem.text)

    def tree(self):
        tree = etree.Element("config")
        tree.set("name", self.name)
        if self.ide:
            tree.set("ide", self.ide)
        if self.host:
            tree.set("host", "true")
        env_tree = self.env.tree()
        tree.append(env_tree)
        cmake_tree = self.cmake.tree()
        tree.append(cmake_tree)
        if self.toolchain:
            toolchain_elem = etree.SubElement(tree, "toolchain")
            toolchain_elem.text = self.toolchain
        profiles_elem = etree.SubElement(tree, "profiles")
        for profile in self.profiles:
            profile_elem = etree.SubElement(profiles_elem, "profile")
            profile_elem.text = profile

        return tree

    def __str__(self):
        res = self.name
        res += "\n"
        if self.host:
            res += "  (host config)\n"
        if self.ide:
            res += "  ide: %s\n" % self.ide
        env_str = str(self.env)
        if env_str:
            res += ui.indent(env_str)
            res += "\n"
        cmake_str = str(self.cmake)
        if cmake_str:
            res += ui.indent(cmake_str)
            res += "\n"
        if self.toolchain:
            res += ui.indent("toolchain: " + self.toolchain)
            res += "\n"
        if self.profiles:
            res += ui.indent("profiles: " + ", ".join(self.profiles))
            res += "\n"
        return res


class QiBuildConfig(object):
    """ A class to represent both local and global
    qibuild.xml configuration files

    """
    def __init__(self):
        self.tree = etree.ElementTree()
        self.defaults = Defaults()

        # Set by self.read_local_config()
        self.local = LocalSettings()

        # A dict of possible configs
        self.configs = dict()

        # A dict of possible IDE
        self.ides = dict()

        # A dicf of server name -> access:
        self.servers = dict()

        # Active env:
        self.env = Env()

        # Active IDE:
        self.ide = None

        # Active CMake config:
        self.cmake = CMake()

        # A dict of worktree, key being the path
        self.worktrees = dict()

    def read(self, cfg_path=None, create_if_missing=False):
        """ Read from a config location

        """
        if not cfg_path:
            cfg_path = get_global_cfg_path()
        if create_if_missing:
            if not os.path.exists(cfg_path):
                dirname = os.path.dirname(cfg_path)
                qisys.sh.mkdir(dirname, recursive=True)
                with open(cfg_path, "w") as fp:
                    fp.write('<qibuild />\n')
        ui.debug("Reading config from", cfg_path)
        try:
            self.tree.parse(cfg_path)
        except Exception, e:
            mess  = "Could not parse config from %s\n" % cfg_path
            mess += "Error was: %s" % str(e)
            raise Exception(mess)

        # Parse defaults:
        defaults_tree = self.tree.find("defaults")
        if defaults_tree is not None:
            self.defaults.parse(defaults_tree)

        # Parse configs:
        config_trees = self.tree.findall("config")
        for config_tree in config_trees:
            config = BuildConfig()
            config.parse(config_tree)
            self.configs[config.name] = config

        # Parse IDES:
        ide_trees = self.tree.findall("ide")
        for ide_tree in ide_trees:
            ide = IDE()
            ide.parse(ide_tree)
            self.ides[ide.name] = ide

        # Parse servers:
        server_trees = self.tree.findall("server")
        for server_tree in server_trees:
            server = Server()
            server.parse(server_tree)
            self.servers[server.name] = server

        # Parse worktrees
        worktree_trees = self.tree.findall("worktree")
        for worktree_tree in worktree_trees:
            worktree = WorkTree()
            worktree.parse(worktree_tree)
            self.worktrees[worktree.path] = worktree

        self.cmake.generator = self.defaults.cmake.generator
        self.env.bat_file = self.defaults.env.bat_file
        self.env.editor = self.defaults.env.editor
        self.env.path = self.defaults.env.path
        self.ide = None

        current_ide = self.defaults.ide
        if current_ide:
            matching_ide = self.ides.get(current_ide)
            if matching_ide:
                self.ide = matching_ide

    def read_local_config(self, local_xml_path):
        """ Apply a local configuration """
        local_tree = etree.parse(local_xml_path)
        self.local.parse(local_tree)
        default_config = self.local.defaults.config
        if default_config:
            self.set_active_config(default_config)

    def write_local_config(self, local_xml_path):
        """ Dump local settings to a xml file """
        local_tree = self.local.tree()
        qisys.qixml.write(local_tree, local_xml_path)

    def set_active_config(self, config):
        """ Merge various configs from <defaults> and the
        selected <config > tag

        """
        # reset to defaults in case set_active_config is called twice
        self.cmake.generator = self.defaults.cmake.generator
        self.env.path = self.defaults.env.path
        self.env.vars = self.defaults.env.vars
        self.env.bat_file = self.defaults.env.bat_file
        self.ide = self.defaults.ide

        matching_config = self.configs.get(config)
        if matching_config:
            # Prepend path from matching_config to self.env.path
            defaults_env_path = self.defaults.env.path
            config_env_path = matching_config.env.path
            if config_env_path:
                self.env.path = config_env_path
                if defaults_env_path:
                    self.env.path += os.path.pathsep + defaults_env_path
            # Set bat file
            if matching_config.env.bat_file:
                self.env.bat_file = matching_config.env.bat_file
            # Set cmake settings from current config
            if matching_config.cmake.generator:
                self.cmake.generator = matching_config.cmake.generator
            # Set ide from current config
            matching_config_ide = matching_config.ide
            if matching_config_ide:
                if self.ides.get(matching_config_ide):
                    self.ide = self.ides[matching_config_ide]
            # Update env.vars:
            self.env.vars.update(matching_config.env.vars)

    def set_default_config(self, name):
        """ Set a new config to use by default

        """
        self.local.defaults.config = name

    def set_default_ide(self, name):
        """ Set a new IDE to use by default

        """
        self.defaults.ide = name

    def set_default_editor(self, editor):
        """ Set a new editor to use by default
        (Useful for qibuild config --edit)

        """
        self.defaults.editor = editor

    def add_config(self, config):
        """ A a new config to the list

        """
        self.configs[config.name] = config

    def add_ide(self, ide):
        """ Add a new IDE to the list

        """
        if not ide.name:
            raise Exception("ide.name cannot be None")
        self.ides[ide.name] = ide

    def add_to_default_path(self, to_add):
        """ Add a path to the default env path

        """
        default_env_path = self.defaults.env.path
        if default_env_path:
            splitted_paths = default_env_path.split(os.pathsep)
        else:
            splitted_paths = list()
        to_add = qisys.sh.to_native_path(to_add)
        if to_add not in splitted_paths:
            splitted_paths.insert(0, to_add)
        self.defaults.env.path = os.pathsep.join(splitted_paths)

    def add_worktree(self, path):
        if path in self.worktrees:
            return
        to_add = WorkTree()
        to_add.path = path
        self.worktrees[path] = to_add

    def get_server_access(self, server_name):
        """ Return the access settings of a server

        """
        server = self.servers.get(server_name)
        ui.debug("access for", server_name, ":", server)
        if not server:
            return None
        return server.access

    def set_server_access(self, server_name, username,
                            password=None, root=None):
        """ Configure access to a server """
        server = self.servers.get(server_name)
        if not server:
            server = Server()
            server.name = server_name
            self.servers[server_name] = server
        access = self.servers[server_name].access
        access.name = server_name
        access.username = username
        access.password = password
        access.root = root

    def get_default_config_for_worktree(self, worktree_path):
        """ Return the default configuration associated with the given
        worktree

        """
        worktree = self.worktrees.get(worktree_path)
        if not worktree:
            return None
        return worktree.defaults.config

    def set_default_config_for_worktree(self, worktree_path, name):
        """ Set the default configuration for the given worktree

        """
        worktree = self.worktrees.get(worktree_path)
        if not worktree:
            worktree = WorkTree()
            worktree.path = worktree_path
            self.worktrees[worktree.path] = worktree
        worktree.defaults.config = name

    def set_host_config(self, config_name):
        """ Set the config used to build host tools """
        if not config_name in self.configs:
            raise Exception("No such config: %s" % config_name)
        # Make sure that we unset the previous 'host' config when
        # called twice with different config names
        for name, config in self.configs.iteritems():
            if name == config_name:
                config.host = True
            else:
                config.host = False

    def get_host_config(self):
        """ Get the config to use when looking for host tools """
        for name, config in self.configs.iteritems():
            if config.host:
                return name

    def write(self, xml_path=None):
        """ Write back the new config

        """
        if not xml_path:
            xml_path = get_global_cfg_path()

        def get_name(x):
            " helper functions to sort elements "
            return x.name

        qibuild_tree = etree.Element("qibuild")
        qibuild_tree.set("version", "1")
        defaults_tree = self.defaults.tree()
        qibuild_tree.append(defaults_tree)
        configs = self.configs.values()
        configs.sort(key=get_name)
        for config in configs:
            config_tree = config.tree()
            qibuild_tree.append(config_tree)
        ides = self.ides.values()
        ides.sort(key=get_name)
        for ide in ides:
            ide_tree = ide.tree()
            qibuild_tree.append(ide_tree)
        servers = self.servers.values()
        for server in servers:
            server_tree = server.tree()
            qibuild_tree.append(server_tree)
        worktrees = self.worktrees.values()
        for worktree in worktrees:
            worktree_tree = worktree.tree()
            qibuild_tree.append(worktree_tree)

        qisys.qixml.write(qibuild_tree, xml_path)

    def __str__(self):
        res = ""
        defaults_str = str(self.defaults)
        if defaults_str:
            res += "defaults:\n"
            res += ui.indent(defaults_str) + "\n"
            res += "\n"
        configs = self.configs.values()
        configs.sort(key=operator.attrgetter('name'))
        if configs:
            res += "configs:\n"
            for config in configs:
                res += ui.indent(str(config))
                res += "\n"
            res += "\n"
        ides = self.ides.values()
        ides.sort(key=operator.attrgetter('name'))
        if ides:
            res += "ides:\n"
            for ide in ides:
                res += ui.indent(str(ide))
                res += "\n"
            res += "\n"
        servers = self.servers.values()
        servers.sort(key=operator.attrgetter('name'))
        if servers:
            res += "servers:\n"
            for server in servers:
                res += ui.indent(str(server))
                res += "\n"
            res += "\n"
        worktrees = self.worktrees.values()
        worktrees.sort(key=operator.attrgetter('path'))
        if worktrees:
            res += "worktrees:\n"
            for worktree in worktrees:
                res += ui.indent(str(worktree))
                res += "\n"
        return res


class ProjectConfig(object):
    """ A class to read project configuration

    """
    def __init__(self):
        self.name = None
        self.build_depends = set()
        self.run_depends = set()
        self.test_depends = set()
        self.tree = etree.ElementTree()

    def read(self, cfg_path):
        """ Read configuration from an XML file.

        """
        try:
            self.tree.parse(cfg_path)
        except Exception, e:
            mess = "Could not parse config from %s\n" % cfg_path
            mess += "Error was: %s" % str(e)
            raise Exception(mess)

        # Read name
        root = self.tree.getroot()
        if root.tag != "project":
            qisys.qixml.raise_parse_error("Root node must be 'project'",
                xml_path=cfg_path)
        name = root.get("name")
        if not name:
            qisys.qixml.raise_parse_error("'project' node must have a 'name' attribute",
                xml_path=cfg_path)
        self.name = name

        # Read depends:
        depends_trees = self.tree.findall("depends")
        for depends_tree in depends_trees:
            buildtime = qisys.qixml.parse_bool_attr(depends_tree, "buildtime")
            runtime   = qisys.qixml.parse_bool_attr(depends_tree, "runtime")
            testtime  = qisys.qixml.parse_bool_attr(depends_tree, "testtime")
            dep_names = qisys.qixml.parse_list_attr(depends_tree, "names")
            for dep_name in dep_names:
                if buildtime:
                    self.build_depends.add(dep_name)
                if runtime:
                    self.run_depends.add(dep_name)
                if testtime:
                    self.test_depends.add(dep_name)

    def write(self, location):
        """ Write configuration back to a config file

        """
        project_tree = self.tree.getroot()
        if not project_tree:
            project_tree = etree.Element("project")
            self.tree = etree.ElementTree(element=project_tree)
        project_tree.set("name", self.name)

        for depend_elem in project_tree.findall("depends"):
            project_tree.remove(depend_elem)

        build_elem = etree.Element("depends")
        build_elem.set("buildtime", "true")
        build_elem.set("runtime", "false")
        build_elem.set("testtime", "false")
        build_elem.set("names", " ".join(self.build_depends))
        project_tree.append(build_elem)

        run_elem = etree.Element("depends")
        run_elem.set("buildtime", "false")
        run_elem.set("runtime", "true")
        run_elem.set("testtime", "false")
        run_elem.set("names", " ".join(self.run_depends))
        project_tree.append(run_elem)

        test_elem = etree.Element("depends")
        test_elem.set("buildtime", "false")
        test_elem.set("runtime", "false")
        test_elem.set("testtime", "true")
        test_elem.set("names", " ".join(self.test_depends))
        project_tree.append(test_elem)


        qisys.qixml.write(self.tree, location)

    def __str__(self):
        res = ""
        res += self.name
        if self.build_depends:
            res += "\n"
            res += "  build dependencies: \n"
            for dep in self.build_depends:
                res += ui.indent(dep, num=4)
                res += "\n"
        if self.run_depends:
            res += "  runtime dependencies: \n"
            for dep in self.run_depends:
                res += ui.indent(dep, num=4)
                res += "\n"
        if self.test_depends:
            res += "  test time dependencies: \n"
            for dep in self.test_depends:
                res += ui.indent(dep, num=4)
                res += "\n"
        return res

    def __eq__(self, other):
        return other.name == self.name and \
                other.build_depends == self.build_depends and \
                other.run_depends == self.run_depends and \
                other.test_depends == self.test_depends

    def __ne__(self, other):
        return not self.__eq__(other)


def get_build_env():
    """ Return the build environnment as read from
    qibuild config file

    """
    qibuild_cfg = QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    envsetter = qisys.envsetter.EnvSetter()
    envsetter.read_config(qibuild_cfg)
    return envsetter.get_build_env()

def add_build_config(name, toolchain=None, profiles=None,
                     ide=None, cmake_generator=None, host=False):
    """ Add a new build config to the list """
    qibuild_cfg = QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)

    if name in qibuild_cfg.configs:
        build_config = qibuild_cfg.configs[name]
    else:
        build_config = BuildConfig()
    build_config.name = name
    build_config.toolchain = toolchain
    if profiles:
        build_config.profiles = profiles
    if cmake_generator:
        build_config.cmake.generator = cmake_generator
    if ide:
        build_config.ide = ide
    build_config.host = host
    qibuild_cfg.add_config(build_config)
    qibuild_cfg.write()

def get_config_names():
    qibuild_cfg = QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    return qibuild_cfg.configs.keys()
