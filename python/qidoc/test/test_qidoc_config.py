## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Automatic testing for qidoc.config

"""

from StringIO import StringIO
import unittest

import qidoc.config

class QiDocConfigTestCase(unittest.TestCase):
    def test_simple_parse(self):
        xml = """
<qidoc>
  <repo name="qibuild">
    <sphinxdoc name="qibuild" src="doc" />
  </repo>

  <repo name="libnaoqi" >
    <doxydoc name="libalcommon" src="libalcommon/doc" />
    <doxydoc name="libalvision" src="libalvision/doc" />
  </repo>

  <repo name="doc">
    <sphinxdoc name="doc" src="source" dest="." />
  </repo>

  <defaults root_project ="doc" />

  <templates>
    <doxygen
      doxyfile="soure/tools/Doxyfile.template"
      css="soure/tools/doxygen.template.css"
      header="soure/tools/header.template.html"
      footer="soure/tools/footer.template.html"
    />
    <sphinx
      config="source/conf.py"
      themes ="source/_themes"
    />
  </templates>

</qidoc>
"""
        cfg_path = StringIO(xml)
        qidoc_cfg = qidoc.config.parse(cfg_path)

        self.assertEqual(qidoc_cfg.defaults.root_project, "doc")
        repos = qidoc_cfg.repos

        qibuild_repo = repos[0]
        self.assertEqual(qibuild_repo.name,   "qibuild")
        self.assertEqual(len(qibuild_repo.sphinxdocs), 1)
        qibuild_sphinx = qibuild_repo.sphinxdocs[0]
        self.assertEqual(qibuild_sphinx.name, "qibuild")
        self.assertEqual(qibuild_sphinx.src , "doc")

        libnaoqi = repos[1]
        self.assertEqual(libnaoqi.name, "libnaoqi")
        self.assertEqual(len(libnaoqi.doxydocs), 2)
        libalcommon = libnaoqi.doxydocs[0]
        libalvision = libnaoqi.doxydocs[1]
        self.assertEqual(libalcommon.name, "libalcommon")
        self.assertEqual(libalvision.name, "libalvision")
        self.assertEqual(libalcommon.src , "libalcommon/doc")
        self.assertEqual(libalvision.src , "libalvision/doc")
        self.assertEqual(libalcommon.dest, "libalcommon")
        self.assertEqual(libalvision.dest, "libalvision")



if __name__ == "__main__":
    unittest.main()
