#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" CMake Builder """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import hashlib
import operator
import functools

import qisys.sh
import qisys.remote
from qisys import ui
from qisys.abstractbuilder import AbstractBuilder
import qibuild.deps
import qibuild.deploy
from qibuild.project import write_qi_path_conf
from qibuild.parallel_builder import ParallelBuilder


def md5_checksum(file_path):
    """ Compute the md5 checksum of the given file """
    m = hashlib.md5()
    chunksize = 1024*1024
    with open(file_path, 'rb') as fh:
        while True:
            data = fh.read(chunksize)
            if not data:
                break
            m.update(data)
    fh.close()
    return m.hexdigest()


class CMakeBuilder(AbstractBuilder):
    """
    CMake driver.
    Allow building multiple cmake projects together.
    Dependencies can optionally be resolved and taken into account.
    """

    def __init__(self, build_worktree, projects=None):
        """ CMakeBuilder Init """
        super(CMakeBuilder, self).__init__(self.__class__.__name__)
        self.build_worktree = build_worktree
        if not projects:
            self.projects = list()
        else:
            self.projects = projects
        self.deps_solver = qibuild.deps.DepsSolver(build_worktree)
        self.dep_types = ["build", "runtime", "test"]

    @property
    def dep_types(self):
        """ The list of dependencies to use """
        return self.deps_solver.dep_types

    @dep_types.setter
    def dep_types(self, value):
        """ Dependencies Setter """
        self.deps_solver.dep_types = value

    @property
    def build_config(self):
        """ The :py:class:`.CMakeBuildConfig` to use when building projects """
        return self.build_worktree.build_config

    @property
    def build_env(self):
        """ The environment used when building projects """
        return self.build_config.build_env

    @property
    def toolchain(self):
        """ The :py:class:`.Toolchain` to use when building """
        return self.build_config.toolchain

    def need_configure(func):
        """ Decorator for every function that expects a build directory to exist. """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            """ Function Wrapper """
            projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
            for project in projects:
                if not os.path.exists(project.cmake_cache):
                    raise NotConfigured(project)
            res = func(self, *args, **kwargs)
            return res
        return new_func

    def bootstrap_projects(self):
        """ Write the dependencies.cmake and the qi/path.conf files for every project. """
        projects = self.deps_solver.get_dep_projects(self.projects,
                                                     ["build", "runtime", "test"])
        # subtle diffs here: dependencies.cmake must be written for *all* projects,
        # with the build dependencies
        for project in projects:
            sdk_dirs = self.get_sdk_dirs_for_project(project)
            host_dirs = self.get_host_dirs(project)
            project.write_dependencies_cmake(sdk_dirs, host_dirs=host_dirs)
        qi_path_sdk_dirs = [p.sdk_directory for p in self.build_worktree.build_projects]
        if self.toolchain:
            qi_path_sdk_dirs.extend(package.path for package in self.toolchain.packages)
        # path.conf must be written right before cmake is called, and with
        # all the dependencies
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        for project in projects:
            write_qi_path_conf(project.sdk_directory, qi_path_sdk_dirs)
        # also write a path.conf in the .qi directory
        write_qi_path_conf(self.build_worktree.dot_qi, qi_path_sdk_dirs, sdk_layout=False)

    def get_sdk_dirs_for_project(self, project):
        """ Get SDL Dir For Project """
        sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build", "test"])
        # remove this when all qiproject.xml have been fixed
        strict_mode = os.environ.get("QIBUILD_STRICT_DEPS_RESOLUTION")
        if strict_mode:
            packages = self.deps_solver.get_dep_packages([project], ["build"])
        else:
            if self.toolchain:
                packages = self.toolchain.packages
            else:
                packages = list()
        sdk_dirs.extend([package.path for package in packages])
        return sdk_dirs

    def get_host_dirs(self, project):
        """ Get Host Dirs """
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
                    raise Exception(mess.format(matching_project=matching_project.name))
            else:
                # No project, try a package in the toolchain
                toolchain = self.build_worktree.toolchain
                if toolchain:
                    matching_package = toolchain.get_package(host_dep, raises=False)
                    if matching_package:
                        res.append(matching_package.path)
        return res

    def pre_build(self, project):
        """ Called before building a project. """
        sdk_dirs = self.deps_solver.get_sdk_dirs(project,
                                                 ["build", "runtime", "test"])
        paths = sdk_dirs[:]
        packages = self.deps_solver.get_dep_packages([project],
                                                     ["build", "runtime", "test"])
        paths.extend([package.path for package in packages])
        project.fix_shared_libs(paths)

    def configure(self, *args, **kwargs):
        """ Configure the projects in the correct order. """
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
                          ui.blue, project.name)
            project.configure(**kwargs)

    @need_configure
    def build(self, *args, **kwargs):
        """ Build the projects in the correct order. """
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Building",
                          ui.blue, project.name,
                          ui.green, "in",
                          ui.blue, project.build_type,
                          update_title=True)
            self.pre_build(project)
            project.build(**kwargs)

    def build_parallel(self, *args, **kwargs):
        """ Build the projects (in parallel) in the correct order. """
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        # do the prebuild step here (it is fast enough)
        for project in projects:
            self.pre_build(project)
        parallel_builder = ParallelBuilder()
        parallel_builder.prepare_build_jobs(projects)
        parallel_builder.build(*args, **kwargs)

    @need_configure
    def install(self, dest, *args, **kwargs):
        """ Install the projects and the packages to the dest dir """
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
        real_dest = os.path.join(dest, prefix)
        components = kwargs.get("components")
        build_type = "Release"
        if projects:
            ui.info(ui.green, "The following projects")
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
            ui.info(ui.green, ":: Installing packages")
        for i, package in enumerate(packages):
            ui.info_count(i, len(packages),
                          ui.green, "Installing", ui.blue, package.name,
                          ui.green, "to", ui.blue, dest,
                          update_title=True)
            files = package.install(real_dest, components=components,
                                    release=release)
            installed.extend(files)
        # Remove qitest.json so that we don't append tests twice
        # when running qibuild install --with-tests twice
        qitest_json = os.path.join(dest, "qitest.json")
        qisys.sh.rm(qitest_json)
        if projects:
            ui.info(ui.green, ":: Installing projects")
            for i, project in enumerate(projects):
                ui.info_count(i, len(projects),
                              ui.green, "Installing", ui.blue, project.name,
                              ui.green, "to", ui.blue, dest,
                              update_title=True)
                files = project.install(dest, **kwargs)
                installed.extend(files)
        replace_dup_lib_simlinks = True
        if sys.platform.startswith("win"):
            replace_dup_lib_simlinks = False
        elif os.environ.get('QIBUILD_DONT_OPTIMIZE_PKG_SIZE'):
            replace_dup_lib_simlinks = False
        return self.post_install(
            dest,
            installed,
            replace_duplicated_lib_by_symlink=replace_dup_lib_simlinks,
            remove_python_bytecode=not os.environ.get("QIBUILD_KEEP_PYTHON_BYTECODE")
        )

    @staticmethod
    def post_install(dest, installed, replace_duplicated_lib_by_symlink=False, remove_python_bytecode=False):
        """
        Run post install optimizations like:
            - replace duplicated libs by a symlink
            - remove python bytecode (*.pyc, *.pyo)
        :param str dest: Installation directory
        :param list installed: List on installed files (path is relative to installation directory
        :param bool replace_duplicated_lib_by_symlink: If False, skip the symlink optimization
        :param bool remove_python_bytecode: If False, skrip the python bytecode removal
        """
        ui.info("Post install step")
        if replace_duplicated_lib_by_symlink and sys.platform.startswith("win"):
            ui.warning("Cannot perform lib deduplication on Windows")
            replace_duplicated_lib_by_symlink = False
        duplicated = {}
        clean_installed = set()
        for fic in installed:
            full_path = os.path.join(dest, fic)
            if replace_duplicated_lib_by_symlink and os.path.split(fic)[0] == 'lib' and '.so' in os.path.basename(fic)\
                    and not os.path.islink(full_path):
                fingerprint = md5_checksum(full_path)
                if fingerprint not in duplicated:
                    duplicated[fingerprint] = set()
                duplicated[fingerprint].add(fic)
            elif os.path.splitext(fic)[1] in (".pyc", ".pyo") and remove_python_bytecode:
                ui.info("Removing bytecode", full_path)
                qisys.sh.rm(full_path)
            else:
                clean_installed.add(fic)
        for _, files in duplicated.items():
            clean_installed = clean_installed.union(files)
            if len(files) > 1:
                keep_this_one = None
                for fic in sorted(files, reverse=True):
                    full_path = os.path.join(dest, fic)
                    if not keep_this_one:
                        keep_this_one = full_path
                        ui.info("Found duplicated lib {} ({} times)".format(fic, len(files) - 1))
                    else:
                        target = os.path.join('.', os.path.relpath(keep_this_one, os.path.dirname(full_path)))
                        ui.info(" - {} -> {}".format(full_path, target))
                        qisys.sh.rm(full_path)
                        qisys.sh.ln(target, full_path)
        return list(clean_installed)

    @need_configure
    def deploy(self, url, split_debug=False, with_tests=False, install_tc_packages=True):
        """ Deploy the project and the packages it depends to a remote url """
        to_deploy = list()
        dep_projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        dep_packages = self.deps_solver.get_dep_packages(self.projects, self.dep_types)
        if not install_tc_packages:
            dep_packages = list()
        # Deploy packages: install all of them in the same temp dir, then
        # deploy this temp dir to the target
        deploy_name = self.build_config.build_directory(prefix="deploy")
        deploy_dir = os.path.join(self.build_worktree.root, ".qi", deploy_name)
        if not os.path.isdir(deploy_dir):
            qisys.sh.mkdir(deploy_dir)
        deploy_manifest = os.path.join(deploy_dir, "deploy_manifest.txt")
        if os.path.exists(deploy_manifest):
            qisys.sh.rm(deploy_manifest)
        components = ["runtime"]
        if with_tests:
            components.append("test")
        # Remove qitest.json so that we don't append tests twice
        # when running `qibuild deploy --with-tests` twice
        qitest_json = os.path.join(deploy_dir, "qitest.json")
        qisys.sh.rm(qitest_json)
        ui.info(ui.green, "The following projects")
        for project in sorted(dep_projects, key=operator.attrgetter("name")):
            ui.info(ui.green, " *", ui.reset, ui.blue, project.name)
        if dep_packages:
            ui.info(ui.green, "and the following packages")
            for package in sorted(dep_packages, key=operator.attrgetter("name")):
                ui.info(ui.green, " *", ui.reset, ui.blue, package.name)
        ui.info(ui.green, "will be deployed to", ui.blue, url.as_string)
        if dep_packages:
            ui.info(ui.green, ":: Deploying packages")
            for i, package in enumerate(dep_packages):
                ui.info_count(i, len(dep_packages),
                              ui.green, "Deploying package", ui.blue, package.name,
                              ui.green, "to", ui.blue, url.as_string,
                              update_title=True)
                # Install package in local deploy dir
                files = package.install(deploy_dir, components=components)
                to_deploy.extend(files)
        ui.info(ui.green, ":: Deploying projects")
        # Deploy projects: install them inside a 'deploy' dir in the worktree
        # root, then deploy this dir to the target
        for (i, project) in enumerate(dep_projects):
            ui.info_count(i, len(dep_projects),
                          ui.green, "Deploying project", ui.blue, project.name,
                          ui.green, "to", ui.blue, url.as_string,
                          update_title=True)
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
            to_deploy = sorted(list(set(to_deploy)))
            f.write("\n".join(to_deploy))
        ui.info(ui.green, "::", "Syncing to url", ui.reset, ui.bold,
                url.as_string, update_title=True)
        qisys.remote.deploy(deploy_dir, url, filelist=deploy_manifest)


class NotConfigured(Exception):
    """ NotConfigured Exception """

    def __init__(self, project):
        """ NotConfigured Init """
        super(NotConfigured, self).__init__()
        self.project = project

    def __str__(self):
        """ String Representation """
        mess = """The project {project.name} has not been configured yet.\nPlease run `qibuild configure` first\n"""
        return mess.format(project=self.project)
