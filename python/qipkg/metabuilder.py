## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import copy
import os
import zipfile

from qisys import ui
import qipkg.metapackage
import qipkg.builder

class MetaPMLBuilder(object):
    """ Build a meta package from a mpml file """

    def __init__(self, mpml_path, worktree=None):
        ui.info(ui.green, "::", ui.reset, ui.bold,
                "Reading", mpml_path, "\n")
        self.worktree = worktree
        self.mpml_path = mpml_path
        self.meta_package = qipkg.metapackage.MetaPackage(self.worktree, self.mpml_path)
        self.pml_builders = list()
        pml_paths = self.meta_package.pml_paths
        for pml_path in pml_paths:
            pml_builder = qipkg.builder.PMLBuilder(pml_path, worktree=worktree)
            self.pml_builders.append(pml_builder)

    def configure(self):
        """ Configure every project """
        n = len(self.pml_builders)
        for i, pml_builder in enumerate(self.pml_builders):
            ui.info(ui.green, "::", ui.reset, ui.bold, "[%i/%i]" % ((i + 1), n),
                    "Configuring", pml_builder.pml_path)
            pml_builder.configure()

    def build(self):
        """ Build every project """
        n = len(self.pml_builders)
        for i, pml_builder in enumerate(self.pml_builders):
            ui.info(ui.green, "::", ui.reset, ui.bold, "[%i/%i]" % ((i + 1), n),
                    "Building", pml_builder.pml_path)
            pml_builder.build()

    def install(self, dest):
        """ Install every project to the given destination """
        n = len(self.pml_builders)
        for i, pml_builder in enumerate(self.pml_builders):
            ui.info(ui.green, "::", ui.reset, ui.bold, "[%i/%i]" % ((i + 1), n),
                    "Installing", pml_builder.pml_path)
            pml_builder.install(dest)

    def deploy(self, url):
        """ Deploy every project to the given url """
        n = len(self.pml_builders)
        for i, pml_builder in enumerate(self.pml_builders):
            ui.info(ui.green, "::", ui.reset, ui.bold, "[%i/%i]" % ((i + 1), n),
                    "Deploying", pml_builder.pml_path)
            pml_builder.deploy(url)

    def make_package(self, with_breakpad=False, output=None):
        """ Generate a package containing every package.

        :param: with_breakpad generate debug symbols for usage
                               with breakpad

        """
        all_packages = list()
        n = len(self.pml_builders)
        for i, pml_builder in enumerate(self.pml_builders):
            ui.info(ui.green, "::", ui.reset, ui.bold, "[%i/%i]" % ((i + 1), n),
                    "Making package from", pml_builder.pml_path)
            packages = pml_builder.make_package(with_breakpad=with_breakpad)
            all_packages.extend(packages)
        if not output:
            name = self.meta_package.name
            version = self.meta_package.version
            if version:
                output = "%s-%s.mpkg" % (name, version)
            else:
                output = "%s.mpkg" % name
        archive = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)
        for package in all_packages:
            archive.write(package, arcname=os.path.basename(package))
        archive.close()
        ui.info(ui.green, "::", ui.reset, ui.bold, "Meta package generated in", output)
        return output
