## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


""" Read / write qibuild configuration file

"""

import os
HAS_LXML = False
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    from xml.etree import ElementTree as etree
from StringIO import StringIO

import qibuild

def raise_parse_error(message, cfg_path=None, tree=None):
    """ Raise a nice parsing error about the given
    tree element

    """
    as_str = etree.tostring(tree)
    mess = ""
    if cfg_path:
        mess += "Error when parsing '%s'\n" % cfg_path
    if tree:
        mess += "Could not parse:\t%s\n" % as_str
    mess += message
    raise Exception(mess)

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

class IDE:
    def __init__(self):
        self.name = None
        self.path = None

    def parse(self, tree):
        name = tree.get("name")
        if not name:
            raise_parse_error("ide node should have a name attribute",
                tree=tree)
        self.name = name
        self.path = tree.get("path")

    def tree(self):
        tree = etree.Element("ide")
        tree.set("name", self.name)
        if self.path:
            tree.set("path", self.path)
        return tree


class Build:
    def __init__(self):
        self.incredibuild = False
        self.build_dir = None
        self.sdk_dir   = None

    def parse(self, tree):
        incredibuild = tree.get("incredibuild")
        if incredibuild and incredibuild.lower() in ["y", "yes", "1", "true", "on"]:
            self.incredibuild = True
        build_dir = tree.get("build_dir")
        if build_dir:
            self.build_dir = qibuild.sh.to_native_path(build_dir)
        # Not calling to_native_path because sdk_dir can be
        # relative to the worktree
        self.sdk_dir = tree.get("sdk_dir")

    def tree(self):
        tree = etree.Element("build")
        if self.build_dir:
            tree.set("build_dir", self.build_dir)
        if self.sdk_dir:
            tree.set("sdk_dir", self.sdk_dir)
        if self.incredibuild:
            tree.set("incredibuild", "true")
        return tree

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

class Defaults:
    def __init__(self):
        # A config name to use by default
        self.config = None
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
        self.config = tree.get("config")
        self.ide    = tree.get("ide")


    def tree(self):
        tree = etree.Element("defaults")
        if self.config:
            tree.set("config", self.config)
        if self.ide:
            tree.set("ide", self.ide)
        env_tree = self.env.tree()
        tree.append(env_tree)
        cmake_tree = self.cmake.tree()
        tree.append(cmake_tree)
        return tree

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
            raise_parse_error("'config' node must have a 'name' attribute",
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


class QiBuildConfig:

    def __init__(self, user_config=None):
        self.tree = etree.ElementTree()
        self.defaults = Defaults()
        self.build = Build()
        self.manifest = None
        self.user_config = user_config

        # A dict of possible configs
        self.configs = dict()

        # A dict of possible IDE
        self.ides = dict()

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

    def read(self, config_location):
        """ Read from a config location

        """
        try:
            self.tree.parse(config_location)
        except Exception, e:
            mess  = "Could not parse config from %s\n" % config_location
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

        # Parse manifest settings:
        manifest_tree = self.tree.find("manifest")
        if manifest_tree is not None:
            self.manifest = Manifest()
            self.manifest.parse(manifest_tree)

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

        self.merge_configs()

    def merge_configs(self):
        """ Merge various configs

        """
        default_config = self.defaults.config
        if self.user_config:
            self.active_config = self.user_config
        else:
            if default_config:
                self.active_config = default_config

        self.env.bat_file = self.defaults.env.bat_file
        self.env.editor   = self.defaults.env.editor
        self.cmake        = self.defaults.cmake
        self.ide          = None

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
                self.env.bat_file = matching_config.env.bat_file
                # Set cmake settings from current config
                self.cmake = matching_config.cmake
                # Set ide from current config
                matching_config_ide = matching_config.ide
                if matching_config_ide:
                    if self.ides.get(matching_config_ide):
                        self.ide = self.ides[matching_config_ide]


    def set_default_config(self, name):
        """ Set a new config to use by default

        """
        self.defaults.config = name

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
        self.ides[ide.name] = ide


    def set_manifest_url(self, manifest_url):
        """ Set a manifest url to use

        """
        if not self.manifest:
            self.manifest = Manifest()
        self.manifest.url = manifest_url

    def write(self, location):
        """ Write back the new config

        """
        def get_name(x):
            " helper functions to sort elements "
            return x.name

        qibuild_tree = etree.Element("qibuild")
        if self.manifest:
            manifest_tree = self.manifest.tree()
            qibuild_tree.append(manifest_tree)
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

        tree = etree.ElementTree(element=qibuild_tree)
        if HAS_LXML:
            # pylint: disable-msg=E1123
            tree.write(location, pretty_print=True)
        else:
            tree.write(location)

class ProjectConfig:
    """ A class to read project configuration

    """
    def __init__(self):
        self.name = None
        self.depends = list()
        self.rdepends = list()
        self.tree = etree.ElementTree()

    def read(self, cfg_path):
        """ Read configuration from an XML file

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
            raise_parse_error("Root node must be 'project'",
                cfg_path=cfg_path)
        name = root.get("name")
        if not name:
            raise_parse_error("'project' node must have a 'name' attribute",
                cfg_path=cfg_path)
        self.name = name

        # Read depends:
        depends_trees = self.tree.findall("depends")
        for depends_tree in depends_trees:
            depends_name = depends_tree.get("name")
            if not depends_name:
                raise_parse_error("'depends' node must have a 'name' attribute",
                    cfg_path=cfg_path,
                    tree=depends_tree)
            self.depends.append(depends_name)

        # Read rdepends:
        rdepends_trees = self.tree.findall("rdepends")
        for rdepends_tree in rdepends_trees:
            rdepends_name = rdepends_tree.get("name")
            if not rdepends_name:
                raise_parse_error("'rdepends' node must have a 'name' attribute",
                    cfg_path=cfg_path,
                    tree=rdepends_tree)
            self.rdepends.append(rdepends_name)




def convert_qibuild_cfg(qibuild_cfg):
    """ Convert an old qibuild.cfg file
    into a new qibuild.xml file

    """
    ini_cfg = qibuild.configstore.ConfigStore()
    ini_cfg.read(qibuild_cfg)
    qibuild_cfg = QiBuildConfig()
    general_config = ini_cfg.get("general.config")
    if general_config:
        qibuild_cfg.defaults.config = general_config
    cmake_generator = ini_cfg.get("general.cmake.generator")
    if cmake_generator:
        qibuild_cfg.defaults.cmake.generator = cmake_generator
    env_editor = ini_cfg.get("general.env.editor")
    if env_editor:
        qibuild_cfg.defaults.env.editor = env_editor
    env_path = ini_cfg.get("general.env.path")
    if env_path:
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
        qibuild_cfg.build.build_dir = build_dir
    sdk_dir = ini_cfg.get("general.build.sdk_dir")
    if sdk_dir:
        qibuild_cfg.build.sdk_dir = sdk_dir
    incredibuild_str = ini_cfg.get("general.build.incredibuild", default="")
    if incredibuild_str.lower() in ["y", "yes", "1", "true", "on"]:
            qibuild_cfg.build.incredibuild = True

    manifest_url = ini_cfg.get("manifest.url")
    if manifest_url:
        manifest = Manifest()
        manifest.url = manifest_url
        qibuild_cfg.manifest = manifest

    for (name, _) in ini_cfg.get("config", default=dict()).iteritems():
        config = Config()
        config.name = name
        cmake_generator = ini_cfg.get("config.%s.cmake.generator" % name)
        if cmake_generator:
            config.cmake.generator = cmake_generator
        qibuild_cfg.configs[config.name] = config

    out = StringIO()
    qibuild_cfg.write(out)

    return out.getvalue()



def convert_project_manifest(qibuild_manifest):
    """ Convert a on qibuild.manifest file
    (ini format) into a new qibuild.manifest
    file (xml format)

    """
    ini_cfg = qibuild.configstore.ConfigStore()
    ini_cfg.read(qibuild_manifest)
    p_names = ini_cfg.get("project", default=dict()).keys()
    if len(p_names) != 1:
        raise_parse_error("File should countain exactly one [project] section",
            cfg_path=qibuild_manifest)
    name = p_names[0]
    project = ProjectConfig()
    project.name = name
    depends  = ini_cfg.get("project.%s.depends"  % name, default="").split()
    rdepends = ini_cfg.get("project.%s.rdepends" % name, default="").split()
    project.depends  = depends[:]
    project.rdepends = rdepends[:]
    out = StringIO()
    project.write(out)
    return out.getvalue()
