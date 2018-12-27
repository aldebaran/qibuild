#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Licence """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.qixml
from qisys import ui
from qisys.qixml import etree


def read_license(xml_path):
    """ Read the license from a qiproject.xml file """
    if not os.path.exists(xml_path):
        ui.warning(""" Could not read license.\n{0} does not exists\n""".format(xml_path), end="")
        return None
    root = qisys.qixml.read(xml_path).getroot()
    license_elem = root.find("license")
    if license_elem is None:
        ui.warning(
            """ The xml file in {0} does not define any license.
Please edit this file to silence this warning\n""".format(xml_path),
            end=""
        )
        return None
    return license_elem.text


def write_license(xml_path, license_):
    """ Write Licence """
    root = qisys.qixml.read(xml_path).getroot()
    license_elem = root.find("license")
    if license_elem is None:
        license_elem = etree.SubElement(root, "license")
    license_elem.text = license_
    qisys.qixml.write(root, xml_path)
