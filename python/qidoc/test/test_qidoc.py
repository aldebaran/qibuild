## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import tempfile
import unittest

import qidoc.core
import qibuild


class TestQiDoc(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tmp-qidoc")

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_build(self):
        in_dir  = os.path.join(self.tmp, "in")
        out_dir = os.path.join(self.tmp, "out")
        this_dir = os.path.dirname(__file__)
        qibuild.sh.install(os.path.join(this_dir, "in"), in_dir, quiet=True)

        qidoc_builder = qidoc.core.QiDocBuilder(in_dir, out_dir, version="1.14")
        opts = dict()
        qidoc_builder.build(opts)

if __name__ == "__main__":
    unittest.main()
