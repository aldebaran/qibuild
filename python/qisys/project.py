## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" WorkTreeProject object """

import os

import qisys.worktree
import qisys.qixml
from qisys.qixml import etree

import qisrc.license

class WorkTreeProject(object):
    """ A project is identified by its path relative to its
    worktree.

    It can have nested subprojects

    """
    def __init__(self, worktree, src):
        self.worktree = worktree
        self.src = src
        self.subprojects = list()

    @property
    def path(self):
        """Give the path in native form."""
        path = os.path.join(self.worktree.root, self.src)
        return qisys.sh.to_native_path(path)

    @property
    def qiproject_xml(self):
        """Give the path to the qiproject.xml."""
        xml_path = os.path.join(self.path, "qiproject.xml")
        return xml_path

    @property
    def license(self):
        """ The license used by this project """
        return qisrc.license.read_license(self.qiproject_xml)

    @license.setter
    def license(self, value):
        qisrc.license.write_license(self.qiproject_xml, value)

    @property
    def version(self):
        """ The version of this project """
        xml_path = self.qiproject_xml
        if not os.path.exists(xml_path):
            return None
        tree = qisys.qixml.read(xml_path)
        root = tree.getroot()
        version_elem = root.find("version")
        if version_elem is None:
            return None
        return version_elem.text

    @version.setter
    def version(self, value):
        xml_path = self.qiproject_xml
        if not os.path.exists(xml_path):
            with open(xml_path, "w") as fp:
                fp.write('<project format="3"/>\n')
        tree = qisys.qixml.read(xml_path)
        root = tree.getroot()
        version_elem = root.find("version")
        if version_elem is None:
            version_elem = etree.SubElement(root, "version")
        version_elem.text = value
        qisys.qixml.write(tree, xml_path)

    def parse_qiproject_xml(self):
        """ Parse the qiproject.xml, filling the
        subprojects list

        """
        if not os.path.exists(self.qiproject_xml):
            return
        tree = qisys.qixml.read(self.qiproject_xml)
        project_elems = tree.findall("project")
        for project_elem in project_elems:
            sub_src = qisys.qixml.parse_required_attr(project_elem, "src",
                                                      xml_path=self.qiproject_xml)
            if sub_src == ".":
                continue
            full_path = os.path.join(self.path, sub_src)
            if not os.path.exists(full_path):
                raise qisys.worktree.WorkTreeError(""" \
Invalid qiproject.xml detected (in {0})
Found an invalid sub project: {1}
{2} does not exist
""".format(self.qiproject_xml, sub_src, full_path))
            self.subprojects.append(sub_src)

    def __repr__(self):
        return "<WorkTreeProject in %s>" % self.src

    def __eq__(self, other):
        return self.src == other.src

    def __ne__(self, other):
        return not (self.__eq__, other)

    def __hash__(self):
        return hash(self.src)
