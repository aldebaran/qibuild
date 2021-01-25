#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qipkg.metapackage


def test_meta(worktree):
    """ Test Meta """
    tmpdir = worktree.tmpdir
    meta_pml = tmpdir.ensure("meta.mpml", file=True)
    meta_pml.write("""
<metapackage name="meta" version="0.1">
  <include src="a/a.pml" />
  <include src="b/b.mpml" />

</metapackage>
""")
    a_pml = tmpdir.ensure("a/a.pml", file=True)
    a_pml.write("""
<package />
""")
    b_mpml = tmpdir.ensure("b/b.mpml", file=True)
    b_mpml.write("""
<metapackage name="b">
  <include src="c/c.pml" />
</metapackage>
""")
    c_pml = tmpdir.ensure("c/c.pml", file=True)
    c_pml.write("""
<package />
""")
    meta_pml = qipkg.metapackage.MetaPackage(worktree, meta_pml.strpath)
    expected_paths = ["a/a.pml", "c/c.pml"]
    expected_paths = [os.path.join(tmpdir.strpath, x) for x in expected_paths]
    assert meta_pml.pml_paths == expected_paths
