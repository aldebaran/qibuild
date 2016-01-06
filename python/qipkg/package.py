## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import zipfile

import qisys.qixml
from qisys.qixml import etree

def name_from_archive(archive_path):
    archive = zipfile.ZipFile(archive_path)
    xml_data = archive.read("manifest.xml")
    elem = etree.fromstring(xml_data)
    return elem.get("uuid")
