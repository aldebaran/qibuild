## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import functools
import operator

from qisys import ui
import qisys.error
import qisys.sh
import qisys.remote
import qisrc.worktree
import qibuild.deploy
import qibuild.deps
from qibuild.parallel_builder import ParallelBuilder
from qisys.abstractbuilder import AbstractBuilder
from qibuild.project       import write_qi_path_conf

class CMakeBuilder(AbstractBuilder):
    """ CMake driver.
        Allow building multiple cmake projects together.
        Dependencies can optionally be resolved and taken into account.
    """
    def __init__(self, build_worktree, projects=None):
        self.build_worktree = build_worktree
        if not projects:
            self.projects = list()
        else:
            self.projects = projects
        self.deps_solver = qibuild.deps.DepsSolver(build_worktree)
        self.dep_types = ["build", "runtime", "test"]

        # Whether we ignore the qiproject.xml and always look for
        # -config.cmake files in all the packages of the toolchain.
        # Two ways this can be set to 'True'
        #  - setting the QIBUILD_LOOSE_DEPS_RESOLUTION environment variable
        #  - have a setting in qisrc manifest saying so
        self.loose_deps_resolution = False

        git_worktree = qisrc.worktree.GitWorkTree(build_worktree.worktree)
        self.loose_deps_resolution = git_worktree.manifest.loose_deps_resolution
        if os.environ.get("QIBUILD_LOOSE_DEPS_RESOLUTION"):
            self.loose_deps_resolution = True

        if os.environ.get("QIBUILD_STRICT_DEPS_RESOLUTION") in ["1", "true", "on"]:
            self.loose_deps_resolution = False

        if self.loose_deps_resolution:
            ui.warning("You are using qibuild with loose dependency "
                       "resolution. It means your qiproject.xml may not be correct")

    # pylint: disable-msg=E0202
    @property
    def dep_types(self):
        """ The list of dependencies to use """
        return self.deps_solver.dep_types

    # pylint: disable-msg=E1101
    @dep_types.setter
    # pylint: disable-msg=E0102
    def dep_types(self, value):
        self.deps_solver.dep_types = value

    @property
    def build_config(self):
        """ The :py:class:`.CMakeBuildConfig` to use when building projects

        """
        return self.build_worktree.build_config

    @property
    def build_env(self):
        """ The environment used when building projects

        """
        return self.build_config.build_env

    @property
    def toolchain(self):
        """ The :py:class:`.Toolchain` to use when building """
        return self.build_config.toolchain

    # pylint: disable-msg=E0213
    def need_configure(func):
        """ Decorator for every function that expects a build directory to
        exist

        """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
            for project in projects:
                if not os.path.exists(project.cmake_cache) and not project.meta:
                    raise NotConfigured(project)
            # pylint: disable-msg=E1102
            res = func(self, *args, **kwargs)
            return res
        return new_func

    def bootstrap_projects(self):
        """ Write the dependencies.cmake and the qi/path.conf files for
        every project

        """
        projects = self.deps_solver.get_dep_projects(self.projects,
                                                     ["build", "runtime", "test"])
        # subtle diffs here: dependencies.cmake must be written for *all* projects,
        # with the build dependencies
        for project in projects:
            sdk_dirs = self.get_sdk_dirs_for_project(project)
            host_dirs = self.get_host_dirs(project)
            if not project.meta:
                project.write_dependencies_cmake(sdk_dirs, host_dirs=host_dirs)

    def get_sdk_dirs_for_project(self, project):
        sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build", "test"])
        if self.loose_deps_resolution:
            if self.toolchain:
                packages = self.toolchain.packages
            else:
                packages = list()
        else:
            packages = self.deps_solver.get_dep_packages([project], ["build"])
        sdk_dirs.extend([package.path for package in packages])
        return sdk_dirs

    def get_host_dirs(self, project):
        res = list()
        host_deps = project.host_depends
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read(create_if_missing=True)
        host_config = qibuild_cfg.get_host_config()
        for host_dep in host_deps:
            matching_project = self.build_worktree.get_build_project(host_dep,
                                                                     raises=False)
            if matching_project:
                host_sdk_dir = matching_project.get_host_sdk_dir()
                res.append(host_sdk_dir)
                if not os.path.exists(host_sdk_dir):
                    mess = """\
Host SDK dir for project {matching_project} does not exist.
Make sure to configure and build it first.
"""
                    mess = mess.format(matching_project=matching_project.name)
                    if host_config:
                        mess += " (Using '%s' build config)" % host_config
                    else:
                        mess += """\
Either set a host config with `qibuild set-host-config`
Or configure the project with no config
"""
                    raise qisys.error.Error(
                            mess.format(matching_project=matching_project.name))
            else:
                # No project, try a package in the toolchain
                toolchain = self.build_worktree.toolchain
                if toolchain:
                    matching_package = toolchain.get_package(host_dep, raises=False)
                    if matching_package:
                        res.append(matching_package.path)

        return res

    def pre_build(self, project):
        """ Called before building a project """
        sdk_dirs = self.deps_solver.get_sdk_dirs(project,
                ["build", "runtime", "test"])
        paths = sdk_dirs[:]
        packages = self.deps_solver.get_dep_packages([project],
                ["build", "runtime", "test"])
        paths.extend([package.path for package in packages])
        project.fix_shared_libs(paths)

    def configure(self, *args, **kwargs):
        """ Configure the projects in the correct order """
        self.bootstrap_projects()
        if kwargs.get("single"):
            projects = self.projects
        else:
            projects = self.deps_solver.get_dep_projects(self.projects,
                                                        ["build", "runtime", "test"])
        # Make sure to not pass the 'single' option to project.configure()
        kwargs.pop("single", None)

        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Configuring",
                          ui.blue, project.name,
                          update_title=True)
            if project.meta:
                ui.info("Meta project, skipping configure")
                continue

            # Make sure CMake is always re-run when on the top projects (it's
            # only ok to skip configure of the dependencies)
            kwargs["allow_cmake_skip"] = (project not in self.projects)

            project.configure(**kwargs)

    @need_configure
    def build(self, *args, **kwargs):
        """ Build the projects in the correct order """
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        for i, project in enumerate(projects):
            mess = [ui.green, "Building", ui.blue, project.name]
            if project.build_type:
                mess.extend(["in", ui.blue, project.build_type])
            ui.info_count(i, len(projects), *mess, update_title=True)
            if project.meta:
                ui.info("Meta project, skipping build")
                continue
            self.pre_build(project)
            project.build(**kwargs)

    def build_parallel(self, *args, **kwargs):
        """ Build the projects (in parallel) in the correct order """
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        # do the prebuild step here (it is fast enough)
        for i, project in enumerate(projects):
            self.pre_build(project)

        parallel_builder = ParallelBuilder()
        parallel_builder.prepare_build_jobs(projects)
        parallel_builder.build(*args, **kwargs)

    @need_configure
    def install(self, dest_dir, *args, **kwargs):
        """ Install the projects and the packages to the dest_dir """
        installed = list()
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        packages = self.deps_solver.get_dep_packages(self.projects, self.dep_types)
        if "install_tc_packages" in kwargs:
            install_tc_packages = kwargs["install_tc_packages"]
            del kwargs["install_tc_packages"]
            if not install_tc_packages:
                packages = list()

        # Compute the real path where to install the packages:
        prefix = kwargs.get("prefix", "/")
        prefix = prefix[1:]
        real_dest = os.path.join(dest_dir, prefix)
        components = kwargs.get("components")

        build_type = "Release"
        if projects:
            ui.info(ui.green, "the following projects")
            for project in projects:
                ui.info(ui.green, " *", ui.blue, project.name)
            if packages:
                ui.info(ui.green, "and the following packages")
                for package in packages:
                    ui.info(ui.green, " *", ui.blue, package.name)
            ui.info(ui.green, "will be installed to", ui.blue, real_dest)

            runtime_only = self.dep_types == ["runtime"]
            if runtime_only:
                ui.info(ui.green, "(runtime components only)")
            build_type = projects[0].build_type

        release = build_type == "Release"
        if packages:
            ui.info(ui.green, ":: ", "installing packages")
        for i, package in enumerate(packages):
            ui.info_count(i, len(packages),
                          ui.green, "Installing",
                          ui.blue, package.name,
                          update_title=True)
            files = package.install(real_dest, components=components,
                                    release=release)
            installed.extend(files)

        # Remove qitest.json so that we don't append tests twice
        # when running qibuild install --with-tests twice
        qitest_json = os.path.join(dest_dir, "qitest.json")
        qisys.sh.rm(qitest_json)

        if projects:
            ui.info(ui.green, ":: ", "installing projects")
            for i, project in enumerate(projects):
                ui.info_count(i, len(projects),
                            ui.green, "Installing",
                            ui.blue, project.name,
                            update_title=True)
                if project.meta:
                    ui.info("Meta project, skipping install")
                    continue
                files = project.install(dest_dir, **kwargs)
                installed.extend(files)
        return installed


    @need_configure
    def deploy(self, url, split_debug=False, with_tests=False, install_tc_packages=True):
        """ Deploy the project and the packages it depends to a remote url """

        # Deploy packages: install all of them in the same temp dir, then
        # deploy this temp dir to the target
        deploy_name = self.build_config.build_directory(prefix="deploy")
        deploy_dir = os.path.join(self.build_worktree.root, ".qi", deploy_name)
        if not os.path.isdir(deploy_dir):
            qisys.sh.mkdir(deploy_dir)
        deploy_manifest = os.path.join(deploy_dir, "deploy_manifest.txt")
        if os.path.exists(deploy_manifest):
            qisys.sh.rm(deploy_manifest)
        to_deploy = list()
        components = ["runtime"]
        if with_tests:
            components.append("test")

        # Remove qitest.json so that we don't append tests twice
        # when running `qibuild deploy --with-tests` twice
        qitest_json = os.path.join(deploy_dir, "qitest.json")
        qisys.sh.rm(qitest_json)

        if install_tc_packages:
            dep_packages = self.deps_solver.get_dep_packages(self.projects,
                                                             self.dep_types)
        else:
            dep_packages = list()
        dep_projects = self.deps_solver.get_dep_projects(self.projects,
                                                         self.dep_types)
        ui.info(ui.green, "The following projects")
        for project in sorted(dep_projects, key=operator.attrgetter("name")):
            ui.info(ui.green, " *", ui.reset, ui.blue, project.name)
        if dep_packages:
            ui.info(ui.green, "and the following packages")
            for package in sorted(dep_packages, key=operator.attrgetter("name")):
                ui.info(ui.green, " *", ui.reset, ui.blue, package.name)
        ui.info(ui.green, "will be deployed to", ui.blue, url.as_string)

        if dep_packages:
            print
            ui.info(ui.green, ":: ", "Deploying packages")
            for i, package in enumerate(dep_packages):
                ui.info_count(i, len(dep_packages),
                    ui.green, "Deploying package", ui.blue, package.name,
                    ui.green, "to", ui.blue, url.as_string,
                    update_title=True)
                # Install package in local deploy dir
                files = package.install(deploy_dir, components=components)
                to_deploy.extend(files)

        print
        ui.info(ui.green, ":: ", "Deploying projects")
        # Deploy projects: install them inside a 'deploy' dir in the worktree
        # root, then deploy this dir to the target

        for (i, project) in enumerate(dep_projects):
            ui.info_count(i, len(dep_projects),
                    ui.green, "Deploying project", ui.blue, project.name,
                    ui.green, "to", ui.blue, url.as_string,
                    update_title=True)
            if project.meta:
                ui.info("Meta project, skipping deploy")
                continue

            if with_tests:
                to_deploy.append("qitest.json")
            # Install project in local deploy dir
            installed = project.install(deploy_dir, components=components,
                                        split_debug=split_debug)
            to_deploy.extend(installed)
        # Add debugging scripts
        for project in self.projects:
            scripts = qibuild.deploy.generate_debug_scripts(self, deploy_dir,
                                                            project.name, url)
            if scripts:
                to_deploy.extend(scripts)

        # Write the list of files to be deployed
        with open(deploy_manifest, "a") as f:
            # sort and remove duplicates:
            to_deploy = list(set(to_deploy))
            to_deploy.sort()
            f.write("\n".join(to_deploy))

        print
        ui.info(ui.green, "::", "Syncing to url", ui.reset, ui.bold,
                url.as_string, update_title=True)
        qisys.remote.deploy(deploy_dir, url, filelist=deploy_manifest)

        print

class NotConfigured(qisys.error.Error):
    def __init__(self, project):
        self.project = project

    def __str__(self):
        mess = """\
The project {project.name} has not been configured yet.
Please run `qibuild configure` first
"""
        return mess.format(project=self.project)
