## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

from qisys import ui
from qisys.qixml import etree
import qisys.qixml


def read_license(xml_path):
    """ Read the license from a qiproject.xml file """
    if not os.path.exists(xml_path):
        ui.warning(""" Could not read license.
{0} does not exists
""".format(xml_path), end="")
        return None
    root = qisys.qixml.read(xml_path).getroot()
    license_elem = root.find("license")
    if license_elem is None:
        ui.warning(
""" The xml file in {0} does not define any license.
Please edit this file to silence this warning
""".format(xml_path), end="")
    else:
        return license_elem.text

def write_license(xml_path, license_):
    root = qisys.qixml.read(xml_path).getroot()
    license_elem = root.find("license")
    if license_elem is None:
        license_elem = etree.SubElement(root, "license")
    license_elem.text = license_
    qisys.qixml.write(root, xml_path)
