# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import os
import qisys.qixml
from qisys.qixml import etree


def test_deps_not_translated(qidoc_action, record_messages):
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
