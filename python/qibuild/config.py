## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" Read / write qibuild configuration file

"""

import os
import operator

from StringIO import StringIO

import qibuild
import qixml
from qixml import etree


def get_global_cfg_path():
    """ Get path to global config file

    """
    res = "~/.config/qi/qibuild.xml"
    res = qibuild.sh.to_native_path(res)
    return res

def indent(text, num=1):
    """ Helper for __str__ methods

    """
    return "\n".join(["  " * num + l for l in text.splitlines()])



# Using hand-written 'class to xml' stuff is not that
# hard and actually works quite well

class Env:
    def __init__(self):
        self.path = None
        self.bat_file = None
        self.editor = None

    def parse(self, tree):
        self.path = tree.get("path")
        self.bat_file = tree.get("bat_file")
        self.editor   = tree.get("editor")

    def tree(self):
        tree = etree.Element("env")
        if self.path:
            tree.set("path", self.path)
        if self.bat_file:
            tree.set("bat_file", self.bat_file)
        if self.editor:
            tree.set("editor", self.editor)
        return tree

    def __str__(self):
        res = ""
        if self.path:
            res += "env.path: %s\n" % self.path
        if self.bat_file:
            res += "env.bat_file: %s\n"  % self.bat_file
        if self.editor:
            res += "env.editor: %s\n"  % self.editor
        return res

class IDE:
    def __init__(self):
        self.name = None
        self.path = None

    def parse(self, tree):
        name = tree.get("name")
        if not name:
            qixml.raise_parse_error("ide node should have a name attribute",
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


class Build:
    def __init__(self):
        self.incredibuild = False

    def parse(self, tree):
        self.incredibuild = qixml.parse_bool_attr(tree, "incredibuild")

    def tree(self):
        tree = etree.Element("build")
        if self.incredibuild:
            tree.set("incredibuild", "true")
        return tree

    def __str__(self):
        res = ""
        if self.incredibuild:
            res += "incredibuild: %s\n" % self.incredibuild
        return res

class CMake:
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

class Manifest:
    def __init__(self):
        self.url = None

    def parse(self, tree):
        self.url = tree.get("url")

    def tree(self):
        tree = etree.Element("manifest")
        if self.url:
            tree.set("url", self.url)
        return tree

    def __str__(self):
        res = ""
        if self.url:
            res += "url: %s\n" % self.url
        return res

class Defaults:
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
        self.ide    = tree.get("ide")

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
            res += indent(cmake_str) + "\n"
        env_str = str(self.env)
        if env_str:
            res += indent(env_str) + "\n"
        return res

class Access:
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

class Server:
    def __init__(self):
        self.name = None
        self.access = Access()

    def parse(self, tree):
        name = tree.get("name")
        if not name:
            qixml.raise_parse_error("server node should have a name attribute",
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
            res += indent(access_str)
        return res

class LocalSettings:
    def __init__(self):
        self.defaults = LocalDefaults()
        self.build = LocalBuild()
        self.manifest = None

    def parse(self, tree):
        defaults_tree = tree.find("defaults")
        if defaults_tree is not None:
            self.defaults.parse(defaults_tree)
        build_tree = tree.find("build")
        if build_tree is not None:
            self.build.parse(build_tree)
        manifest_tree = tree.find("manifest")
        if manifest_tree is not None:
            self.manifest = Manifest()
            self.manifest.parse(manifest_tree)

    def tree(self):
        tree = etree.Element("qibuild")
        tree.set("version", "1")
        tree.append(self.defaults.tree())
        tree.append(self.build.tree())
        if self.manifest:
            tree.append(self.manifest.tree())
        return tree

    def __str__(self):
        res = ""
        defaults_str = str(self.defaults)
        if defaults_str:
            res += "default settings for this worktree:\n"
            res += indent(defaults_str) + "\n"
        build_str = str(self.build)
        if build_str:
            res += "build settings for this worktree:\n"
            res += indent(build_str) + "\n"
        manifest_str = str(self.manifest)
        if manifest_str:
            res += "qisrc manifest:\n"
            res += indent(manifest_str) + "\n"
        return res


class LocalDefaults:
    def __init__(self):
        # An config name to use by default
        self.config = None
        # A profile to use by default
        self.profile = None

    def parse(self, tree):
        self.config = tree.get("config")
        self.profile = tree.get("profile")

    def tree(self):
        tree = etree.Element("defaults")
        if self.config:
            tree.set("config", self.config)
        if self.profile:
            tree.set("profile", self.profile)
        return tree

    def __str__(self):
        res = ""
        if self.config:
            res += "default config: %s\n" % self.config
        if self.profile:
            res += "default profile: %s\n" % self.profile
        return res

class LocalBuild:
    def __init__(self):
        self.sdk_dir = None
        self.build_dir = None

    def parse(self, tree):
        # Not calling to_native_path because build_dir and sdk_dir can be
        # relative to the worktree
        self.build_dir = tree.get("build_dir")
        self.sdk_dir = tree.get("sdk_dir")

    def tree(self):
        tree = etree.Element("build")
        if self.build_dir:
            tree.set("build_dir", self.build_dir)
        if self.sdk_dir:
            tree.set("sdk_dir", self.sdk_dir)
        return tree

    def __str__(self):
        res = ""
        if self.build_dir:
            res += "build_dir: %s\n" % self.build_dir
        if self.sdk_dir:
            res += "sdk_dir: %s\n" % self.sdk_dir
        return res


class Config:
    def __init__(self):
        self.name  = None
        # The name of an ide
        self.ide = None
        self.env = Env()
        self.cmake = CMake()

    def parse(self, tree):
        name = tree.get("name")
        if not name:
            qixml.raise_parse_error("'config' node must have a 'name' attribute",
                tree=tree)
        self.name = name
        self.ide = tree.get("ide")
        env_tree = tree.find("env")
        if env_tree is not None:
            self.env.parse(env_tree)
        cmake_tree = tree.find("cmake")
        if cmake_tree is not None:
            self.cmake.parse(cmake_tree)

    def tree(self):
        tree = etree.Element("config")
        tree.set("name", self.name)
        if self.ide:
            tree.set("ide", self.ide)
        env_tree  = self.env.tree()
        tree.append(env_tree)
        cmake_tree = self.cmake.tree()
        tree.append(cmake_tree)
        return tree

    def __str__(self):
        res = self.name
        res += "\n"
        if self.ide:
            res += "  ide: %s\n" % self.ide
        env_str = str(self.env)
        if env_str:
            res += indent(env_str)
            res += "\n"
        cmake_str = str(self.cmake)
        if cmake_str:
            res += indent(cmake_str)
            res += "\n"
        return res



class QiBuildConfig:
    """ A class to represent both local and global
    qibuild.xml configuration files

    """
    def __init__(self, user_config=None):
        self.tree = etree.ElementTree()
        self.defaults = Defaults()
        self.build = Build()
        self.user_config = user_config

        # Set by self.read_local_config()
        self.local = LocalSettings()

        # A dict of possible configs
        self.configs = dict()

        # A dict of possible IDE
        self.ides = dict()

        # A dicf of server name -> access:
        self.servers = dict()

        # Either: None (in the general case)
        #         The default config as read in the config file
        #         The config set by the user
        self.active_config = None

        # Active env:
        self.env     = Env()

        # Active IDE:
        self.ide    = None

        # Active CMake config:
        self.cmake  = CMake()

    def read(self, cfg_path=None, create_if_missing=False):
        """ Read from a config location

        """
        if not cfg_path:
            cfg_path = get_global_cfg_path()
            if not os.path.exists(cfg_path):
                if create_if_missing:
                    dirname = os.path.dirname(cfg_path)
                    qibuild.sh.mkdir(dirname, recursive=True)
                    with open(cfg_path, "w") as fp:
                        fp.write('<qibuild />\n')
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

        # Parse build settings:
        build_tree = self.tree.find("build")
        if build_tree is not None:
            self.build.parse(build_tree)

        # Parse configs:
        config_trees = self.tree.findall("config")
        for config_tree in config_trees:
            config = Config()
            config.parse(config_tree)
            self.configs[config.name] = config

        # Parse IDES:
        ide_trees = self.tree.findall("ide")
        for ide_tree in ide_trees:
            ide = IDE()
            ide.parse(ide_tree)
            self.ides[ide.name] = ide

        # Parse servers:
        server_trees =  self.tree.findall("server")
        for server_tree in server_trees:
            server = Server()
            server.parse(server_tree)
            self.servers[server.name] = server

        self.merge_configs()

    def read_local_config(self, local_xml_path):
        """ Apply a local configuration """
        local_tree = etree.parse(local_xml_path)
        self.local.parse(local_tree)
        self.merge_configs()

    def write_local_config(self, local_xml_path):
        """ Dump local settings to a xml file """
        local_tree = self.local.tree()
        qixml.write(local_tree, local_xml_path)

    def merge_configs(self):
        """ Merge various configs

        """
        default_config = self.local.defaults.config
        if self.user_config:
            self.active_config = self.user_config
        else:
            if default_config:
                self.active_config = default_config

        self.cmake.generator = self.defaults.cmake.generator
        self.env.bat_file    = self.defaults.env.bat_file
        self.env.editor = self.defaults.env.editor
        self.env.path = self.defaults.env.path
        self.ide = None

        current_ide = self.defaults.ide
        if current_ide:
            matching_ide = self.ides.get(current_ide)
            if matching_ide:
                self.ide = matching_ide

        if self.active_config:
            matching_config = self.configs.get(self.active_config)
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
        (Useful for qibuid config --edit)

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
        to_add = qibuild.sh.to_native_path(to_add)
        if to_add not in splitted_paths:
            splitted_paths.insert(0, to_add)
        self.defaults.env.path = os.pathsep.join(splitted_paths)

    def set_manifest_url(self, manifest_url):
        """ Set a manifest url to use

        """
        if not self.local.manifest:
            self.local.manifest = Manifest()
        self.local.manifest.url = manifest_url

    def get_server_access(self, server_name):
        """ Return the access settings of a server

        """
        server = self.servers.get(server_name)
        if not server:
            return None
        return server.access

    def set_server_access(self, server_name, username, password=None, root=None):
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
        build_tree = self.build.tree()
        qibuild_tree.append(build_tree)
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

        qixml.write(qibuild_tree, xml_path)

    def __str__(self):
        res = ""
        build_str = str(self.build)
        if build_str:
            res += "build:\n"
            res += indent(build_str) + "\n"
            res += "\n"
        defaults_str = str(self.defaults)
        if defaults_str:
            res += "defaults:\n"
            res += indent(defaults_str) + "\n"
            res += "\n"
        configs = self.configs.values()
        configs.sort(key = operator.attrgetter('name'))
        if configs:
            res += "configs:\n"
            for config in configs:
                res += indent(str(config))
                res += "\n"
            res += "\n"
        ides = self.ides.values()
        ides.sort(key = operator.attrgetter('name'))
        if ides:
            res += "ides:\n"
            for ide in ides:
                res += indent(str(ide))
                res += "\n"
            res += "\n"
        servers = self.servers.values()
        servers.sort(key = operator.attrgetter('name'))
        if servers:
            res += "servers:\n"
            for server in servers:
                res += indent(str(server))
                res += "\n"
        return res


class ProjectConfig:
    """ A class to read project configuration

    """
    def __init__(self):
        self.name = None
        self.depends = set()
        self.rdepends = set()
        self.tree = etree.ElementTree()

    def read(self, cfg_path):
        """ Read configuration from an XML file.

        """
        try:
            self.tree.parse(cfg_path)
        except Exception, e:
            mess  = "Could not parse config from %s\n" % cfg_path
            mess += "Error was: %s" % str(e)
            raise Exception(mess)

        # Read name
        root = self.tree.getroot()
        if root.tag != "project":
            qixml.raise_parse_error("Root node must be 'project'",
                xml_path=cfg_path)
        name = root.get("name")
        if not name:
            qixml.raise_parse_error("'project' node must have a 'name' attribute",
                xml_path=cfg_path)
        self.name = name

        # Read depends:
        depends_trees = self.tree.findall("depends")
        for depends_tree in depends_trees:
            buildtime = qixml.parse_bool_attr(depends_tree, "buildtime")
            runtime   = qixml.parse_bool_attr(depends_tree, "runtime")
            dep_names = qixml.parse_list_attr(depends_tree, "names")
            if buildtime:
                for dep_name in dep_names:
                    self.depends.add(dep_name)
            if runtime:
                for dep_name in dep_names:
                    self.rdepends.add(dep_name)

    def write(self, location):
        """ Write configuration back to a config file

        """
        # FIXME: remove existing <depends> element first ...
        project_tree = self.tree.getroot()
        if not project_tree:
            project_tree = etree.Element("project")
            self.tree = etree.ElementTree(element = project_tree)
        project_tree.set("name", self.name)

        both_deps = self.depends.intersection(self.rdepends)
        if both_deps:
            both_deps_tree = etree.Element("depends")
            both_deps_tree.set("buildtime", "true")
            both_deps_tree.set("runtime"  , "true")
            both_deps_tree.set("names", " ".join(both_deps))
            project_tree.append(both_deps_tree)

        runtime_only = self.rdepends - self.depends
        if runtime_only:
            runtime_tree = etree.Element("depends")
            runtime_tree.set("runtime", "true")
            runtime_tree.set("names", " ".join(runtime_only))
            project_tree.append(runtime_tree)

        build_only = self.depends - self.rdepends
        if build_only:
            build_tree = etree.Element("depends")
            build_tree.set("buildtime", "true")
            build_tree.set("names", " ".join(build_only))
            project_tree.append(build_tree)

        qixml.write(self.tree, location)

    def __str__(self):
        res = ""
        res += self.name
        if self.depends:
            res += "\n"
            res += "  depends: \n"
            for depends in self.depends:
                res += indent(depends, 2)
                res += "\n"
        if self.rdepends:
            res += "  rdepends: \n"
            for rdepends in self.rdepends:
                res += indent(rdepends, 2)
                res += "\n"
        return res


def convert_qibuild_cfg(qibuild_cfg):
    """ Convert an old qibuild.cfg file
    into two new strings:
    (global_xml, local_xml)

    """
    ini_cfg = qibuild.configstore.ConfigStore()
    ini_cfg.read(qibuild_cfg)
    qibuild_cfg = QiBuildConfig()
    general_config = ini_cfg.get("general.config")
    if general_config:
        qibuild_cfg.local.defaults.config = general_config
    cmake_generator = ini_cfg.get("general.cmake.generator")
    if cmake_generator:
        qibuild_cfg.defaults.cmake.generator = cmake_generator
    env_editor = ini_cfg.get("general.env.editor")
    if env_editor:
        qibuild_cfg.defaults.env.editor = env_editor
    env_path = ini_cfg.get("general.env.path")
    if env_path:
        env_path = env_path.replace("\n", "")
        qibuild_cfg.defaults.env.path = env_path
    env_bat_file = ini_cfg.get("general.env.bat_file")
    if env_bat_file:
        qibuild_cfg.defaults.env.bat_file = env_bat_file
    env_ide = ini_cfg.get("general.env.ide")
    if env_ide:
        qibuild_cfg.defaults.ide = env_ide
        ide = IDE()
        ide.name = env_ide
        qibuild_cfg.ides[ide.name] = ide
    qtcreator_path = ini_cfg.get("general.env.qtcreator.path")
    if qtcreator_path:
        if not qibuild_cfg.ides.get("QtCreator"):
            qibuild_cfg.ides["QtCreator"] = IDE("QtCreator")
        qibuild_cfg.ides["QtCreator"].path = qtcreator_path
    build_dir = ini_cfg.get("general.build.directory")
    if build_dir:
        qibuild_cfg.local.build.build_dir = build_dir
    sdk_dir = ini_cfg.get("general.build.sdk_dir")
    if sdk_dir:
        qibuild_cfg.local.build.sdk_dir = sdk_dir
    incredibuild_str = ini_cfg.get("general.build.incredibuild", default="")
    if incredibuild_str.lower() in ["y", "yes", "1", "true", "on"]:
        qibuild_cfg.build.incredibuild = True

    manifest_url = ini_cfg.get("manifest.url")
    if manifest_url:
        manifest = Manifest()
        manifest.url = manifest_url
        qibuild_cfg.local.manifest = manifest

    for (name, _) in ini_cfg.get("config", default=dict()).iteritems():
        config = Config()
        config.name = name
        cmake_generator = ini_cfg.get("config.%s.cmake.generator" % name)
        if cmake_generator:
            config.cmake.generator = cmake_generator
        qibuild_cfg.configs[config.name] = config

    out = StringIO()
    qibuild_cfg.write(out)
    global_xml = out.getvalue()

    out = StringIO()
    qibuild_cfg.write_local_config(out)
    local_xml = out.getvalue()

    return (global_xml, local_xml)



def convert_qibuild_xml(xml_path):
    """ Convert from previous version.
    (Between 1.12 and 1.12.1 XML had no 'version' attribute)

    """
    tree = etree.ElementTree()
    tree.parse(xml_path)
    qibuild_cfg = QiBuildConfig()
    qibuild_cfg.read(xml_path)
    qibuild_cfg.read_local_config(xml_path)

    out = StringIO()
    qibuild_cfg.write(out)
    global_xml = out.getvalue()

    out = StringIO()
    qibuild_cfg.write_local_config(out)
    local_xml = out.getvalue()

    return (global_xml, local_xml)


def convert_project_manifest(qibuild_manifest):
    """ Convert a on qibuild.manifest file
    (ini format) into a new qibuild.manifest
    file (xml format)

    """
    ini_cfg = qibuild.configstore.ConfigStore()
    ini_cfg.read(qibuild_manifest)
    p_names = ini_cfg.get("project", default=dict()).keys()
    if len(p_names) != 1:
        qixml.raise_parse_error("File should countain exactly one [project] section",
            xml_path=qibuild_manifest)
    name = p_names[0]
    project = ProjectConfig()
    project.name = name
    depends  = ini_cfg.get("project.%s.depends"  % name, default="").split()
    rdepends = ini_cfg.get("project.%s.rdepends" % name, default="").split()
    project.depends  = set(depends)
    project.rdepends = set(rdepends)
    out = StringIO()
    project.write(out)
    return out.getvalue()


def get_build_env():
    """ Return the build environnment as read from
    qibuild config file

    """
    qibuild_cfg = QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    envsetter = qibuild.envsetter.EnvSetter()
    envsetter.read_config(qibuild_cfg)
    return envsetter.get_build_env()
