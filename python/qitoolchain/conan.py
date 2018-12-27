#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Create a Conan Package with QiBuild tools """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import tempfile
import qisys.sh
import qisys.command
import qisys.interact
from qisys import ui


class Conan(object):
    """ This class create a conan package directory ready to be converted by qitoolchain """

    def __init__(self, name, version, channels=None, is_shared=None):
        """ Conan class allows us to create a conanfile and compile the library with conan."""
        self.name = name
        self.version = version
        self.channels = channels
        self.is_shared = is_shared
        self.temp_dir = None
        self.conanfile = None
        self.package_path = None

    def __del__(self):
        if self.package_path is not None:
            self.clean()

    def create(self):
        """
        Ask conan channel and parameters to create a conanfile and build it
        Tested with: "boost/1.68.0@conan/stable" shared
        """
        if not self.channels:
            question = "Which conan library do you want to add?"
            channel = qisys.interact.ask_string(question, default=True)
            self.channels = [channel]
        if self.is_shared is None:
            question = "Do you want it to be shared (highly recommended)?"
            self.is_shared = qisys.interact.ask_yes_no(question, default=True)
        self.prepare()
        self.write_conanfile()
        self.build()
        return self.package_path

    def prepare(self):
        """ Create a temporary directory where to build the library. """
        self.temp_dir = tempfile.mkdtemp("-qiconan-{}-{}".format(self.name, self.version))
        self.package_path = os.path.join(self.temp_dir, "package")

    def write_conanfile(self):
        """ Write a default conanfile.txt with standard informations """
        assert self.temp_dir, "This build is not ready, please call prepare()"
        self.conanfile = os.path.join(self.temp_dir, "conanfile.txt")
        ui.info(" * Write conanfile in", self.conanfile)
        with open(self.conanfile, "w") as fp:
            fp.write("[requires]" + os.linesep)
            for c in self.channels:
                fp.write(c + os.linesep)
            fp.write(os.linesep)
            fp.write("[options]" + os.linesep)
            for c in self.channels:
                fp.write("{}:shared={}{}".format(c.split('/')[0], self.is_shared, os.linesep))
            fp.write(os.linesep)
            contents = """\
[generators]
json

[imports]
bin, *.dll -> ./bin
lib, *.lib* -> ./lib
lib, *.dylib* -> ./lib
lib, *.so* -> ./lib
lib, *.a* -> ./lib
include, * -> ./include
"""
            fp.write(contents)

    def build(self):
        """ Call conan command to build the package with the conanfile """
        ui.info(" * Building library with conan in", self.package_path)
        qisys.command.check_is_in_path("conan")
        conan_path = qisys.command.find_program("conan")
        cmd = [conan_path, "install", self.conanfile, "--build", "--install-folder", self.package_path]
        qisys.command.call(cmd)

    def clean(self):
        """ Remove the temporary directory """
        ui.info(" * Removing temporary directory")
        qisys.sh.rm(self.temp_dir)
