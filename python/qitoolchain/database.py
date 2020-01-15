#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.qixml

from qisys import ui
from qisys.qixml import etree

import qitoolchain.feed
import qitoolchain.qipackage
import qitoolchain.svn_package


class DataBase(object):
    """ Binary Packages Storage """

    def __init__(self, name, db_path):
        """ Binary Packages Storage Init """
        self.name = name
        self.build_target = None
        self.db_path = db_path
        self.packages = dict()
        self.load()
        self.packages_path = qisys.sh.get_share_path("qi", "toolchains", self.name)

    @property
    def target(self):
        """ Build target from the feed """
        return self.build_target

    def load(self):
        """ Load the packages from the xml file """
        tree = qisys.qixml.read(self.db_path)
        self.build_target = tree.getroot().get("target")
        ui.debug("Load target from database xml", self.build_target, "in", self.db_path)
        for element in tree.findall("package"):
            to_add = qitoolchain.qipackage.from_xml(element)
            self.packages[to_add.name] = to_add
        for svn_elem in tree.findall("svn_package"):
            to_add = qitoolchain.qipackage.from_xml(svn_elem)
            self.packages[to_add.name] = to_add

    def save(self):
        """ Save the packages in the xml file """
        root = etree.Element("toolchain")
        if self.build_target:
            root.set("target", self.build_target)
            ui.debug("Save target in database xml", self.build_target, "in", self.db_path)
        tree = etree.ElementTree(root)
        for package in self.packages.values():
            element = package.to_xml()
            root.append(element)
        qisys.qixml.write(tree, self.db_path)

    def remove(self):
        """ Remove self """
        qisys.sh.rm(self.packages_path)
        qisys.sh.rm(self.db_path)

    def add_package(self, package):
        """ Add a package to the database """
        package.load_package_xml()
        package.reroot_paths()
        package.post_add()
        self.packages[package.name] = package

    def remove_package(self, name):
        """ Remove a package from a database """
        if name not in self.packages:
            raise Exception("No such package: %s" % name)
        to_remove = self.packages[name]

        if not to_remove.subpkg:
            qisys.sh.rm(to_remove.path)
        del self.packages[name]

    def get_package_path(self, name):
        """ Get the path to a package given its name """
        if name in self.packages:
            return self.packages[name].path
        return None

    def get_package(self, name, raises=True):
        """ Get a package given its name """
        res = self.packages.get(name)
        if res is None:
            if raises:
                raise Exception("No such package: %s" % name)
        return res

    def solve_deps(self, packages, dep_types=None):
        """ Parse every package.xml, and solve dependencies """
        to_sort = dict()
        for package in self.packages.values():
            package.load_deps()
            deps = set()
            if "build" in dep_types:
                deps.update(package.build_depends)
            if "runtime" in dep_types:
                deps.update(package.run_depends)
            if "test" in dep_types:
                deps.update(package.test_depends)
            to_sort[package.name] = deps
        sorted_names = qisys.sort.topological_sort(to_sort, [x.name for x in packages])
        res = list()
        for name in sorted_names:
            if name in self.packages:
                res.append(self.packages[name])
        return res

    def update(self, feed, branch=None, name=None):
        """
        Update a toolchain given a feed
        ``feed`` can be:
        * a path
        * an url
        * a git url (in this case branch and name cannot be None,
          and ``feeds/<name>.xml`` must exist on the given branch)
        """
        feed_parser = qitoolchain.feed.ToolchainFeedParser(self.name)
        feed_parser.parse(feed, branch=branch, name=name)
        self.build_target = feed_parser.target
        ui.debug("Update target in database from feedParser", self.build_target)
        remote_packages = feed_parser.get_packages()
        local_packages = self.packages.values()
        to_add = list()
        to_remove = list()
        to_update = list()
        svn_packages = [
            x for x in remote_packages
            if isinstance(x, qitoolchain.svn_package.SvnPackage)
        ]
        other_packages = [x for x in remote_packages if x not in svn_packages]
        for remote_package in other_packages:
            if remote_package.name in (x.name for x in local_packages):
                continue
            to_add.append(remote_package)
        for local_package in local_packages:
            if local_package.name not in (x.name for x in remote_packages):
                to_remove.append(local_package)
        remote_names = [x.name for x in remote_packages]
        for local_package in local_packages:
            if local_package not in remote_packages and local_package.name in remote_names:
                remote_package = [x for x in remote_packages
                                  if x.name == local_package.name][0]
                to_update.append(remote_package)
        # remove svn packages from the list of packages to update
        to_update = [
            x for x in to_update
            if not isinstance(x, qitoolchain.svn_package.SvnPackage)
        ]
        if to_update:
            ui.info(ui.red, "Updating packages")
        for i, package in enumerate(to_update):
            remote_package = [x for x in remote_packages if x.name == package.name][0]
            local_package = [x for x in local_packages if x.name == package.name][0]
            ui.info_count(i, len(to_update), ui.blue,
                          package.name, "from", local_package.version,
                          "to", remote_package.version)
            self.remove_package(package.name)
            self.handle_package(package, feed)
            self.add_package(package)
        if to_remove:
            ui.info(ui.red, "Removing packages")
        for i, package in enumerate(to_remove):
            ui.info_count(i, len(to_remove), ui.blue, package.name)
            self.remove_package(package.name)
        if to_add:
            ui.info(ui.green, "Adding packages")
        for i, package in enumerate(to_add):
            ui.info_count(i, len(to_add), ui.blue, package.name)
            self.handle_package(package, feed)
            self.add_package(package)
        if svn_packages:
            ui.info(ui.green, "Updating svn packages")
        for i, svn_package in enumerate(svn_packages):
            ui.info_count(i, len(svn_packages), ui.blue, svn_package.name)
            self.handle_svn_package(svn_package)
            self.add_package(svn_package)
        ui.info(ui.green, "Done")
        self.save()

    def handle_package(self, package, feed):
        """ Download if needed and Handle a Package """
        if package.url:
            self.download_package(package)
        if package.directory:
            self.handle_local_package(package, feed)

    def handle_svn_package(self, svn_package):
        """ Handle an SVN Package """
        dest = os.path.join(self.packages_path, svn_package.name)
        svn_package.path = dest
        if os.path.exists(dest):
            svn_package.update()
        else:
            svn_package.checkout()

    @staticmethod
    def handle_local_package(package, feed):
        """ Handle a Local Package """
        directory = package.directory
        feed_root = os.path.dirname(feed)
        package_path = os.path.join(feed_root, directory)
        package_path = qisys.sh.to_native_path(package_path)
        package.path = package_path

    def download_package(self, package):
        """ Download a Package """
        with qisys.sh.TempDir() as tmp:
            archive = qisys.remote.download(
                package.url,
                tmp,
                message=(ui.green, "Downloading", ui.reset, ui.blue, package.url)
            )
            dest = os.path.join(self.packages_path, package.name)
            message = [ui.green, "Extracting", ui.reset, ui.blue, package.name]
            if package.version:
                message.append(package.version)
            ui.info(*message)
            qitoolchain.qipackage.extract(archive, dest)
        package.path = dest
