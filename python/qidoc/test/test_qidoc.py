## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import tempfile
import unittest

import qidoc.core
import qibuild


def check_tools():
    """ Check if sphinx-build and doxygen are installed.
    If not, we will skip the test_build test

    """
    executables = dict()
    for name in ["sphinx-build", "sphinx-build2", "doxygen"]:
        executables[name] = qibuild.command.find_program(name)

    res = executables["sphinx-build"] or executables["sphinx-build2"]
    res = res and executables["doxygen"]
    return res

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

    @unittest.skipUnless(check_tools(), "Some required tools are not installed")
    def test_build(self):
        opts = dict()
        opts["version"] = 1.42
        self.qidoc_builder.build(opts)
        submodule_zip = os.path.join(self.out_dir,
            "qibuild", "_downloads", "submodule.zip")
        self.assertTrue(os.path.exists(submodule_zip))

    def test_cfg_parse(self):
        qibuild_sphinx = self.qidoc_builder.sphinxdocs["qibuild"]
        self.assertEqual(qibuild_sphinx.name, "qibuild")
        self.assertEqual(qibuild_sphinx.src ,
            os.path.join(self.in_dir, "qibuild", "doc"))

        doc_sphinx = self.qidoc_builder.sphinxdocs["doc"]
        self.assertEqual(doc_sphinx.depends, ["qibuild"])


        libalcommon = self.qidoc_builder.doxydocs["libalcommon"]
        libalvision = self.qidoc_builder.doxydocs["libalvision"]
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
