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


class MetaPackage(object):
    """ Built with a mpml path. Contains a list of pml paths """

    def __init__(self, worktree, mpml_path):
        """ MetaPackage Init """
        self.worktree = worktree
        self.mpml = mpml_path
        self.pml_paths = list()
        self.name = None
        self.version = None
        self.load()

    def load(self):
        """ Load """
        tree = qisys.qixml.read(self.mpml)
        root = tree.getroot()
        if root.tag != "metapackage":
            raise Exception("""\nInvalid mpml %s\nRoot element must be <metapackage>\n""" % self.mpml)
        self.name = qisys.qixml.parse_required_attr(root, "name", xml_path=self.mpml)
        self.version = root.get("version")
        include_elems = root.findall("include")
        for include_elem in include_elems:
            src = qisys.qixml.parse_required_attr(include_elem, "src", xml_path=self.mpml)
            src = os.path.join(self.worktree.root, src)
            if src.endswith(".pml"):
                self.pml_paths.append(src)
            if src.endswith(".mpml"):
                sub_meta = MetaPackage(self.worktree, src)
                self.pml_paths.extend(sub_meta.pml_paths)
