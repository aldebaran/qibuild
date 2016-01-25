## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.sh

from qidoc.test.test_qidoc_build import write_french_po

def test_install_translated(qidoc_action, tmpdir):
    translateme_proj = qidoc_action.add_test_project("translateme")
    qidoc_action("intl-update", "translateme")
    write_french_po(translateme_proj.path)
    qidoc_action("install", "translateme", tmpdir.strpath, "--language", "fr")
    index_html = tmpdir.join("index.html")
    assert "Bienvenue" in index_html.read()

def test_cleans_install_dir(qidoc_action, tmpdir):
    dest = tmpdir.join("dest")
    world_proj = qidoc_action.add_test_project("world")
    index_rst = os.path.join(world_proj.path, "source", "index.rst")
    with open(index_rst, "r") as fp:
        orig_contents = fp.read()
    with open(index_rst, "a") as fp:
        fp.write("""
.. toctree
    world.rst
""")

    world_rst = os.path.join(world_proj.path, "source", "world.rst")
    with open(world_rst, "w") as fp:
        fp.write("Some documentation about the world")

    qidoc_action("install", "world", dest.strpath)
    assert dest.join("index.html").check(file=True)
    assert dest.join("world.html").check(file=True)

    with open(index_rst, "w") as fp:
        fp.write(orig_contents)
    qisys.sh.rm(world_rst)

    qidoc_action("install", "--clean", "world", dest.strpath)
    assert not dest.join("world.html").check(file=True)
    assert dest.join("index.html").check(file=True)

def test_do_not_install_doctrees(tmpdir, qidoc_action):
    dest = tmpdir.join("dest")
    qidoc_action.add_test_project("world")
    qidoc_action("install", "world", dest.strpath)
    assert not dest.join(".doctrees").check(dir=True)
