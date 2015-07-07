## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qidoc.test.test_qidoc_build import write_french_po

def test_install_translated(qidoc_action, tmpdir):
    translateme_proj = qidoc_action.add_test_project("translateme")
    qidoc_action("intl-update", "translateme")
    write_french_po(translateme_proj.path)
    qidoc_action("install", "translateme", tmpdir.strpath, "--language", "fr")
    index_html = tmpdir.join("index.html")
    assert "Bienvenue" in index_html.read()
