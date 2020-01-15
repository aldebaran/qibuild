#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import zipfile

from qisys.qixml import etree


def name_from_archive(archive_path):
    """ Name From Archive """
    archive = zipfile.ZipFile(archive_path, allowZip64=True)
    xml_data = archive.read("manifest.xml")
    elem = etree.fromstring(xml_data)
    return elem.get("uuid")
