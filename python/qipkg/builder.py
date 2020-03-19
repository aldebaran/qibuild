#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Builder for pml files """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import tempfile
import python_minifier

import qisrc.snapshot
import qisrc.worktree
import qipkg.manifest
import qipy.worktree
import qipy.python_builder
import qibuild.breakpad
import qibuild.worktree
import qibuild.cmake_builder
import qilinguist.worktree
import qilinguist.builder
import qilinguist.pml_translator
import qisys.qixml
from qisys import ui


def minify_python(filepath):
    """ Minify a Python File """
    try:
        if not os.path.isfile(filepath):
            return False
        if not filepath.endswith(".py"):
            return False
        print("-- Minifying  %s" % filepath)
        with open(filepath, "r") as fileread:
            filecontent = fileread.read()
        fileread.close()
        filemini = python_minifier.minify(filecontent)
        with open(filepath, "w") as filewrite:
            filewrite.write(filemini)
        filewrite.close()
        return True
    except Exception:
        print("-- Unable to minify %s" % filepath)
    return False


class PMLBuilder(object):
    """ Build a package from a pml file """

    def __init__(self, pml_path, worktree=None):
        """ PMLBuilder Init """
        if not os.path.exists(pml_path):
            raise Exception("%s does not exist" % pml_path)
        self.pml_path = pml_path
        self.base_dir = os.path.dirname(self.pml_path)
        self.worktree = worktree
        if self.worktree:
            self.git_worktree = qisrc.worktree.GitWorkTree(self.worktree)
            self.build_worktree = qibuild.worktree.BuildWorkTree(self.worktree)
            self.cmake_builder = qibuild.cmake_builder.CMakeBuilder(self.build_worktree)
            self.python_worktree = qipy.worktree.PythonWorkTree(self.worktree)
            self.python_builder = qipy.python_builder.PythonBuilder(
                self.python_worktree,
                build_worktree=self.build_worktree)
            self.linguist_worktree = qilinguist.worktree.LinguistWorkTree(self.worktree)
            self.linguist_builder = qilinguist.builder.QiLinguistBuilder()
            self.builders = [self.cmake_builder, self.python_builder, self.linguist_builder]
        else:
            self.git_worktree = None
            self.cmake_builder = None
            self.build_worktree = None
            self.python_builder = None
            self.python_worktree = None
            self.linguist_builder = None
            self.linguist_worktree = None
            self.builders = list()
        # Hack: we don't want to generate symbols from the staged dir
        # unless we have at least one qibuild project
        self.build_project = None
        self._stage_path = None
        self.pml_extra_files = list()

        # Set default manifest file, just in case
        self.manifest_xml = "manifest.xml"

        self.load_pml(pml_path)

        self.manifest_xml = os.path.join(self.base_dir, self.manifest_xml)
        if not os.path.exists(self.manifest_xml):
            raise Exception("%s does not exist" % self.manifest_xml)
        self.pkg_name = pkg_name(self.manifest_xml)

        # read the manifest and validate it
        self.validator = qipkg.manifest.Validator(self.manifest_xml)
        self.validator.print_errors()
        self.validator.print_warnings()

    @property
    def stage_path(self):
        """ Stage Path """
        if self.worktree:
            dot_qi = self.worktree.dot_qi
            build_config = self.cmake_builder.build_config
            name = build_config.build_directory(prefix="qipkg")
            return os.path.join(dot_qi, name)
        else:
            if not self._stage_path:
                self._stage_path = tempfile.mkdtemp()
            return self._stage_path

    def load_pml(self, pml_path):
        """ Load Pml """
        try:
            self._load_pml(pml_path)
        except qisys.worktree.NoSuchProject as e:
            mess = """ Error when parsing {pml_path}\n{mess}\n"""
            raise Exception(mess.format(pml_path=pml_path, mess=str(e)))

    def _load_pml(self, pml_path):
        """ Load Pml """
        for builder in self.builders:
            builder.projects = list()
        tree = qisys.qixml.read(pml_path)
        root = tree.getroot()
        qibuild_elems = root.findall("qibuild")
        if qibuild_elems and not self.worktree:
            raise Exception("<qibuild> tag found but not in a worktree")
        for qibuild_elem in qibuild_elems:
            name = qisys.qixml.parse_required_attr(qibuild_elem, "name", pml_path)
            project = self.build_worktree.get_build_project(name, raises=True)
            self.cmake_builder.projects.append(project)
            self.build_project = project
        qipython_elems = root.findall("qipython")
        if qipython_elems and not self.worktree:
            raise Exception("<qipython> tag found but not in a worktree")
        for qipython_elem in qipython_elems:
            name = qisys.qixml.parse_required_attr(qipython_elem, "name", pml_path)
            project = self.python_worktree.get_python_project(name, raises=True)
            self.python_builder.projects.append(project)
        qilinguist_elems = root.findall("qilinguist")
        if qilinguist_elems and not self.worktree:
            raise Exception("<qilinguist> tag found but not in a worktree")
        for qilinguist_elem in qilinguist_elems:
            name = qisys.qixml.parse_required_attr(qilinguist_elem, "name", pml_path)
            project = self.linguist_worktree.get_linguist_project(name, raises=True)
            self.linguist_builder.projects.append(project)
        manifest = root.find("Manifest")
        if manifest is not None:
            self.manifest_xml = manifest.get("src")
        # For top, ressource, dialog, behavior
        # add stuff to self.pml_extra_files
        behaviors = root.find("BehaviorDescriptions")
        if behaviors is not None:
            for child in behaviors.findall("BehaviorDescription"):
                src = child.get("src")
                full_src = os.path.join(src, "behavior.xar")
                self.pml_extra_files.append(full_src)
        # Dialog
        dialogs = root.find("Dialogs")
        if dialogs is not None:
            for child in dialogs.findall("Dialog"):
                src = child.get("src")
                self.pml_extra_files.append(src)
        # Resources
        resources = root.find("Resources")
        if resources is not None:
            for child in resources.findall("File"):
                src = child.get("src")
                self.pml_extra_files.append(src)
        # Topics
        topics = root.find("Topics")
        if topics is not None:
            for child in topics.findall("Topic"):
                src = child.get("src")
                self.pml_extra_files.append(src)
        errors = list()
        for extra_file in self.pml_extra_files:
            full_path = os.path.join(self.base_dir, extra_file)
            if not os.path.exists(full_path):
                errors.append(extra_file)
        if errors:
            mess = "Some files do not exist\n"
            for error in errors:
                mess += error + "\n"
            raise Exception(mess)

    def configure(self):
        """ Configure every project """
        for builder in self.builders:
            if isinstance(builder, qibuild.cmake_builder.CMakeBuilder):
                builder.dep_types = ["build", "runtime", "test"]
            builder.configure()

    def build(self):
        """ Build every project """
        for builder in self.builders:
            builder.build()

    def install(self, destination, install_tc_packages=False, python_minify=False, with_snapshot=False):
        """ Install every project to the given destination """
        qisys.sh.mkdir(destination, recursive=True)
        # Copy the manifest
        qisys.sh.install(self.manifest_xml,
                         os.path.join(destination, "manifest.xml"))
        # Use every available builder to install
        build_config = None
        for builder in self.builders:
            desc = desc_from_builder(builder)
            if builder.projects:
                ui.info(ui.bold, "-> Adding %s ..." % desc)
            if isinstance(builder, qibuild.cmake_builder.CMakeBuilder):
                builder.dep_types = ["runtime"]
                build_config = builder.build_config
                builder.install(destination, components=["runtime"],
                                install_tc_packages=install_tc_packages)
            else:
                builder.install(destination)
        # Install self.pml_extra_files
        if self.pml_extra_files:
            ui.info(ui.bold, "-> Adding extra files ...")
        for src in self.pml_extra_files:
            full_src = os.path.join(self.base_dir, src)
            rel_src = os.path.relpath(full_src, self.base_dir)
            full_dest = os.path.join(destination, rel_src)
            qisys.sh.install(full_src, full_dest)
            # Minify Python Files if requested
            if python_minify is True:
                extension = os.path.splitext(rel_src)[1].strip().lower()
                if extension == ".py":
                    minify_python(full_dest)
        if with_snapshot:
            ui.info(ui.bold, "-> Generating snapshot ...")
            qisrc.snapshot.generate_snapshot(self.git_worktree,
                                             os.path.join(destination, "snapshot.json"),
                                             deprecated_format=False)
        # Generate and install translations
        ui.info(ui.bold, "-> Generating translations ...")
        pml_translator = qilinguist.pml_translator.PMLTranslator(self.pml_path)
        pml_translator.release(build_config=build_config)
        pml_translator.install(destination)

    def deploy(self, url):
        """ Deploy every project to the given url """
        qisys.remote.deploy(self.stage_path, url)

    def package(self, *args, **kwargs):
        """
        Generate a package containing every project.
        :param: with_breakpad generate debug symbols for usage with breakpad
        :param: force make package even if it does not satisfy default package requirements
        :param install_tc_packages also install toolchain packages
        """
        output = kwargs.get('output', None)
        force = kwargs.get('force', False)
        with_snapshot = kwargs.get('with_snapshot', False)
        with_breakpad = kwargs.get('with_breakpad', False)
        python_minify = kwargs.get('python_minify', False)
        install_tc_packages = kwargs.get('install_tc_packages', False)
        dump_exe = kwargs.get('dump_exe', None)
        strip = kwargs.get('strip', True)
        strip_exe = kwargs.get('strip_exe', None)
        strip_args = kwargs.get('strip_args', None)
        build_config = kwargs.get('build_config', None)
        build_target = None
        if self.cmake_builder and not build_config:
            build_config = self.cmake_builder.build_config
            # NOTE: It force to load toolchain target if set in the feed
            if build_config:
                build_toolchain = build_config.toolchain
                if build_toolchain:
                    ui.debug("Use toolchain target", build_toolchain.target)
            build_target = build_config.target

        # If the package is not valid, do not go further
        if not self.validator.is_valid and not force:
            raise Exception("Given package does not satisfy "
                            "default package requirements.\n"
                            "Use option '--force' to bypass this validation")
        # Make sure self.stage_path exists and is empty
        qisys.sh.rm(self.stage_path)
        qisys.sh.mkdir(self.stage_path, recursive=True)
        if not output:
            if build_target:
                output = os.path.join(os.getcwd(), "{}-{}.pkg".format(self.pkg_name, build_target))
            else:
                output = os.path.join(os.getcwd(), "{}.pkg".format(self.pkg_name))
            ui.debug("With pkg name:", output)

        # Add everything from the staged path
        self.install(self.stage_path, install_tc_packages=install_tc_packages,
                     python_minify=python_minify, with_snapshot=with_snapshot)
        symbols_archive = None
        if with_breakpad and self.build_project:
            ui.info(ui.bold, "-> Generating breakpad symbols ...")
            dirname = os.path.dirname(output)
            ui.debug("Use breakpad build_config:", build_config)
            if build_target:
                symbols_archive = os.path.join(dirname, "{}-symbols-{}.zip".format(self.pkg_name, build_target))
            else:
                symbols_archive = os.path.join(dirname, "{}-symbols.zip".format(self.pkg_name))
            qibuild.breakpad.gen_symbol_archive(base_dir=self.stage_path,
                                                output=symbols_archive,
                                                dump_exe=dump_exe,
                                                strip=strip,
                                                strip_exe=strip_exe,
                                                strip_args=strip_args,
                                                build_config=build_config)
            ui.info(ui.bold, "-> Symbols generated in", symbols_archive)
        ui.info(ui.bold, "-> Package generated in", output, "\n")
        ui.info(ui.bold, "-> Compressing package ...")
        qisys.archive.compress(self.stage_path, output=output, flat=True,
                               display_progress=True)
        qisys.sh.rm(self.stage_path)
        if symbols_archive:
            return [output, symbols_archive]
        return output

    def __repr__(self):
        """ Representation """
        return "<PMLBuilder for %s>" % self.pml_path


def pkg_name(manifest_xml):
    """ Return a string name-version. """
    root = qisys.qixml.read(manifest_xml).getroot()
    uuid = qisys.qixml.parse_required_attr(root, "uuid", xml_path=manifest_xml)
    version = qisys.qixml.parse_required_attr(root, "version",
                                              xml_path=manifest_xml)
    output_name = "%s-%s" % (uuid, version)
    return output_name


def desc_from_builder(builder):
    """ Desc From Builder """
    class_name = builder.__class__.__name__
    if "CMakeBuilder" in class_name:
        return "C++ projects"
    if "Linguist" in class_name:
        return "translations"
    if "Python" in class_name:
        return "Python projects"
    return None
