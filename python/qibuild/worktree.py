import os

import qisys.command
import qisys.worktree
import qibuild.build
import qibuild.build_config
import qibuild.project

class BuildWorkTreeError(Exception):
    pass

class BuildWorkTree(qisys.worktree.WorkTreeObserver):
    """ Stores a list of projects that can be built using CMake

    """
    def __init__(self, worktree):
        self.worktree = worktree
        self.root = self.worktree.root
        self.build_config = qibuild.build_config.CMakeBuildConfig(self)
        self.build_projects = self._load_build_projects()
        worktree.register(self)

    @property
    def qibuild_cfg(self):
        return self.build_config.qibuild_cfg

    @property
    def qibuild_xml(self):
        """ Path to <worktree>/.qi/qibuild.xml
        Will be created if it does not exist

        """
        config_path = os.path.join(self.worktree.dot_qi, "qibuild.xml")
        if not os.path.exists(config_path):
            with open(config_path, "w") as fp:
                fp.write("<qibuild />\n")
        return config_path

    @property
    def toolchain(self):
        """ The toolchain to use """
        return self.build_config.toolchain

    @property
    def default_config(self):
        """ The default config to use """
        return self.build_config.default_config

    def get_build_project(self, name, raises=True):
        """ Get a :py:class:`.BuildProject` given its name """
        for build_project in self.build_projects:
            if build_project.name == name:
                return build_project
        if raises:
            raise BuildWorkTreeError("No such qibuild project: %s" % name)

    def on_project_added(self, project):
        """ Called when a new project has been registered """
        self.build_projects = self._load_build_projects()

    def on_project_removed(self, project):
        """ Called when a build project has been removed """
        self.build_projects = self._load_build_projects()

    def _load_build_projects(self):
        """ Create BuildProject for every buildable project in the
        worktree

        """
        build_projects = list()
        for wt_project in self.worktree.projects:
            if not os.path.exists(wt_project.qiproject_xml):
                continue
            build_project = qibuild.project.BuildProject(self, wt_project)
            build_projects.append(build_project)
        return build_projects

    def configure_build_profile(self, name, flags):
        """ Configure a build profile for the worktree """
        qibuild.profile.configure_build_profile(self.qibuild_xml,
                                                name, flags)


    def remove_build_profile(self, name):
        """ Remove a build profile for this worktree """
        qibuild.profile.remove_build_profile(self.qibuild_xml, name)

    def set_default_config(self, name):
        """ Set the default toolchain for this worktree """
        local_settings = qibuild.config.LocalSettings()
        tree = qisys.qixml.read(self.qibuild_xml)
        local_settings.parse(tree)
        local_settings.defaults.config = name
        tree = local_settings.tree()
        qisys.qixml.write(tree, self.qibuild_xml)

    def set_active_config(self, active_config):
        """ Set the config to use for this worktree
        Should match a toolchain name

        """
        self.build_config.set_active_config(active_config)
