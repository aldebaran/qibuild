#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Convert a Package to QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import json
import qisys.sh
import qisys.qixml
from qisys import ui
from qisys.qixml import etree
import qibuild.cmake.modules
from qibuild.cmake.modules import add_cmake_module_to_archive
from qitoolchain.binary_package import convert_to_qibuild, open_package


def convert_package(package_path, name, interactive=False):
    """ Convert Package """
    dest_dir = os.path.dirname(package_path)
    package = open_package(package_path)
    with qisys.sh.TempDir() as tmp:
        qibuild_package_path = convert_to_qibuild(package, output_dir=tmp)
        add_cmake_module_to_archive(qibuild_package_path, name, interactive=interactive)
        src = os.path.abspath(qibuild_package_path)
        dst = os.path.join(dest_dir, os.path.basename(qibuild_package_path))
        dst = os.path.abspath(dst)
        qisys.sh.mv(src, dst)
        qibuild_package_path = dst
    return qibuild_package_path


def convert_from_conan(package_path, name, version="0.0.1"):
    """ Convert a conan build output directory to a qibuild package """
    conanbuildinfo_json = os.path.join(package_path, "conanbuildinfo.json")
    assert os.path.isfile(conanbuildinfo_json), "{} not found".format(conanbuildinfo_json)
    with open(conanbuildinfo_json, 'r') as f:
        info = json.load(f)

    settings = info.get("settings")
    ui.info(ui.white, "Compiled on {} {} with {} version {}".format(settings.get("os"), settings.get("arch"),
                                                                    settings.get("compiler"),
                                                                    settings.get("compiler.version")))
    ui.info(ui.white, "Compiled in {} with {} ".format(settings.get("build_type"), settings.get("compiler.libcxx")))
    ui.info("Exposed librairies:")
    for n, deps in enumerate(info.get("dependencies")):
        ui.info_count(n, len(info.get("dependencies")), ui.blue, "{}@{}".format(deps.get("name"), deps.get("version")))
        _copy_conan_share_cmake(package_path, deps)
    _add_conan_package_xml(package_path, name, info, version)
    res = _compress_package(package_path, name, settings, version)
    ui.info(ui.green, "Archive generated in", res)
    return res


def _copy_conan_share_cmake(package_path, deps):
    """ Copy qibuild cmake module files """
    name = deps.get("name")
    if not os.path.exists(os.path.join(package_path, "share")):
        ui.info(" -> Create share/")
        os.mkdir(os.path.join(package_path, "share"))
    if not os.path.exists(os.path.join(package_path, "share", "cmake")):
        ui.info(" -> Create share/cmake/")
        os.mkdir(os.path.join(package_path, "share", "cmake"))
    res = qibuild.cmake.modules.generate_cmake_module(package_path, name)
    ui.info(ui.green, "CMake module generated in", ui.reset, ui.bold, res)


def _add_conan_package_xml(package_path, name, info, version):
    """ write an xml file to descibe the package """
    package_xml = os.path.join(package_path, "package.xml")
    ui.info(" -> Create package.xml for {}".format(name))
    root = etree.Element('package')
    root.set("name", name)
    root.set("version", version)
    root.set("target", info.get("settings").get("os"))
    child = etree.Element("licence", text="BSD")
    root.append(child)
    qisys.qixml.write(root, package_xml)


def _compress_package(package_path, name, settings, version):
    """ form the name and create the archive """
    parts = [name, settings.get("os"), settings.get("arch"), version]
    archive_name = "-".join(parts) + ".zip"
    output = os.path.join(os.getcwd(), archive_name)
    return qisys.archive.compress(package_path, flat=True, output=output, quiet=True, display_progress=True)
