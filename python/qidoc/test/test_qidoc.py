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
        self.in_dir  = os.path.join(self.tmp, "in")
        self.out_dir = os.path.join(self.tmp, "out")
        this_dir = os.path.dirname(__file__)
        qibuild.sh.install(os.path.join(this_dir, "in"),
            self.in_dir, quiet=True)
        self.qidoc_builder = qidoc.core.QiDocBuilder(self.in_dir, self.out_dir)

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_build(self):
        opts = dict()
        opts["version"] = 1.42
        self.qidoc_builder.build(opts)

    def test_cfg_parse(self):
        qidoc_cfg = self.qidoc_builder.config

        repos = qidoc_cfg.repos
        qibuild_repo = repos[0]
        self.assertEqual(qibuild_repo.name,   "qibuild")
        self.assertEqual(len(qibuild_repo.sphinxdocs), 1)
        qibuild_sphinx = qibuild_repo.sphinxdocs[0]
        self.assertEqual(qibuild_sphinx.name, "qibuild")
        self.assertEqual(qibuild_sphinx.src ,
            os.path.join(self.in_dir, "qibuild", "doc"))

        doc_sphinx = repos[-1].sphinxdocs[0]
        self.assertEqual(doc_sphinx.depends, ["qibuild"])


        libnaoqi = repos[1]
        self.assertEqual(libnaoqi.name, "libnaoqi")
        self.assertEqual(len(libnaoqi.doxydocs), 2)
        libalcommon = libnaoqi.doxydocs[0]
        libalvision = libnaoqi.doxydocs[1]
        self.assertEqual(libalcommon.name, "libalcommon")
        self.assertEqual(libalvision.name, "libalvision")
        self.assertEqual(libalcommon.src ,
            os.path.join(self.in_dir, "libnaoqi", "libalcommon"))
        self.assertEqual(libalvision.src ,
            os.path.join(self.in_dir, "libnaoqi", "libalvision"))
        self.assertEqual(libalcommon.dest,
            os.path.join(self.out_dir, "ref", "libalcommon"))
        self.assertEqual(libalvision.dest,
            os.path.join(self.out_dir, "ref", "libalvision"))


        self.assertEqual(qidoc_cfg.templates.repo, "aldeb-templates")


    def test_sorting(self):
        docs = self.qidoc_builder.sort_sphinx()
        names = [d.name for d in docs]
        self.assertEqual(names, ['qibuild', 'doc'])

        docs = self.qidoc_builder.sort_doxygen()
        names = [d.name for d in docs]
        self.assertEqual(names, ['libqi', 'libalcommon', 'libalvision'])

    def test_intersphinx_mapping(self):
        mapping = self.qidoc_builder.get_intersphinx_mapping("doc")
        self.assertEqual(mapping,
            {"qibuild": (os.path.join(self.out_dir, "qibuild"),
                         None)}
        )

    def test_doxygen_mapping(self):
        mapping = self.qidoc_builder.get_doxygen_mapping("libalvision")
        expected = {
            os.path.join(self.out_dir, "doxytags", "libalcommon.tag"):
                "../libalcommon",
            os.path.join(self.out_dir, "doxytags", "libqi.tag"):
              "../libqi",
        }
        self.assertEqual(mapping, expected)




if __name__ == "__main__":
    unittest.main()
