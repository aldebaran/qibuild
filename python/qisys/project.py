# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" WorkTreeProject object """

import os

import qisys.worktree
import qisys.qixml

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
