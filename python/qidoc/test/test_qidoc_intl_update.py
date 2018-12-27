#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.qixml
from qisys.qixml import etree


def test_deps_not_translated(qidoc_action, record_messages):
    """ Test Deps Not Translated """
    translateme_proj = qidoc_action.add_test_project("translateme")
    world_proj = qidoc_action.add_test_project("world")
    qiproject_xml = translateme_proj.qiproject_xml
    root = qisys.qixml.read(qiproject_xml).getroot()
    qidoc_elem = root.find("qidoc")
    depends = etree.SubElement(qidoc_elem, "depends")
    depends.set("name", "world")
    qisys.qixml.write(root, qiproject_xml)
    qidoc_action("intl-update", "translateme")
    index_pot = os.path.join(world_proj.path, "source", "locale", "index.pot")
    assert not os.path.exists(index_pot)
    record_messages.reset()
    qidoc_action("intl-update", "world")
    assert record_messages.find("WARN")
