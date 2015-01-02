## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.qixml
import qisys.version

def bump_version(xml_path, version=None):
    tree = qisys.qixml.read(xml_path)
    root = tree.getroot()
    if version is None:
        previous_version = root.get("version")
        version = qisys.version.increment_version(previous_version)
    root.set("version", version)
    qisys.qixml.write(tree, xml_path)

