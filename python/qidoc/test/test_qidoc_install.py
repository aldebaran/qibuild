#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.sh
from qidoc.test.test_qidoc_build import write_french_po


def test_install_translated(qidoc_action, tmpdir):
    """ Test Install Translated """
    translateme_proj = qidoc_action.add_test_project("translateme")
    qidoc_action("intl-update", "translateme")
    write_french_po(translateme_proj.path)
    qidoc_action("install", "translateme", tmpdir.strpath, "--language", "fr")
    index_html = tmpdir.join("index.html")
    assert "Bienvenue" in index_html.read_text("utf-8")


def test_cleans_install_dir(qidoc_action, tmpdir):
    """ Test Clean Install Dir """
    dest = tmpdir.join("dest")
    world_proj = qidoc_action.add_test_project("world")
    index_rst = os.path.join(world_proj.path, "source", "index.rst")
    with open(index_rst, "r") as fp:
        orig_contents = fp.read()
    with open(index_rst, "a") as fp:
        fp.write("""\n.. toctree\n    world.rst\n""")
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
