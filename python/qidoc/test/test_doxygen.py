#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest

import qidoc.doxygen
import qidoc.builder
from qidoc.test.conftest import find_link


def test_read_doxyfile(tmpdir):
    """ Test Read DoxyFile """
    doxyfile = tmpdir.join("Doxyfile")
    doxyfile.write(
        r"""
INPUT  =      foo \
  include/foo.h
# This is a comment
SPAM=eggs
PREDEFINED = "FOO=1"
PREDEFINED += "BAR=0"
""")
    parsed = qidoc.doxygen.read_doxyfile(doxyfile.strpath)
    assert parsed["INPUT"] == "foo   include/foo.h"
    assert parsed["SPAM"] == "eggs"
    assert parsed["PREDEFINED"] == '"FOO=1" "BAR=0"'


def test_bad_doxyfile(tmpdir):
    """ Test Bad DoxyFile """
    doxyfile = tmpdir.join("Doxyfile")
    doxyfile.write(""""\nFOO = 1\nBAR += 2\n""")
    with pytest.raises(Exception) as e:
        qidoc.doxygen.read_doxyfile(doxyfile.strpath)
    assert "does not match" in str(e.value)


def test_appending_values(tmpdir):
    """ Test Appending Values """
    doxyfile = tmpdir.join("Doxyfile")
    contents = """PREDEFINED = "FOO=1"\nPREDEFINED += "BAR=0"\n"""
    doxyfile.write(contents)
    parsed = qidoc.doxygen.read_doxyfile(doxyfile.strpath)
    assert parsed["PREDEFINED"] == '"FOO=1" "BAR=0"'
    generated = tmpdir.join("generated")
    qidoc.doxygen.write_doxyfile(parsed, generated.strpath)
    assert generated.read() == """PREDEFINED = "FOO=1" "BAR=0"\n"""


def test_forced_settings(doc_worktree):
    """ Test Forced Settings """
    foo_dox = doc_worktree.create_doxygen_project("foo")
    foo_dox.configure()
    conf = qidoc.doxygen.read_doxyfile(foo_dox.out_doxyfile)
    assert conf["OUTPUT_DIRECTORY"] == foo_dox.build_dir
    assert conf["GENERATE_LATEX"] == "NO"
    assert conf["GENERATE_XML"] == "YES"
    assert conf["PROJECT_NAME"] == "foo"


def test_rewrite_relative_paths(doc_worktree):
    """ Test Rewrite Relative Path """
    foo_dox = doc_worktree.create_doxygen_project("foo")
    conf = dict()
    conf["INPUT"] = "src/ include/foo"
    conf["EXAMPLE_PATH"] = "example"
    qidoc.doxygen.write_doxyfile(conf, foo_dox.in_doxyfile)
    foo_dox.configure()
    conf = qidoc.doxygen.read_doxyfile(foo_dox.out_doxyfile)
    assert conf["EXAMPLE_PATH"] == os.path.join(foo_dox.path, "example")
    assert conf["INPUT"] == "%s %s" % (
        os.path.join(foo_dox.path, "src/"),
        os.path.join(foo_dox.path, "include/foo")
    )


def test_with_version(doc_worktree):
    """ Test With Version """
    foo_dox = doc_worktree.create_doxygen_project("foo")
    foo_dox.configure(version="1.2.3")
    conf = qidoc.doxygen.read_doxyfile(foo_dox.out_doxyfile)
    assert conf["PROJECT_NUMBER"] == "1.2.3"


def test_ovewrite_name(doc_worktree):
    """ Test Overwrite Name """
    foo_dox = doc_worktree.create_doxygen_project("foo")
    conf = dict()
    conf["PROJECT_NAME"] = "foo_overwrite"
    qidoc.doxygen.write_doxyfile(conf, foo_dox.in_doxyfile)
    foo_dox.configure()
    conf = qidoc.doxygen.read_doxyfile(foo_dox.out_doxyfile)
    assert conf["PROJECT_NAME"] == "foo_overwrite"


def test_depends_on_doxygen(doc_worktree, tmpdir):
    """ Test Depends On DoxyGen """
    _libworld_proj = doc_worktree.add_test_project("libworld")
    libhello_proj = doc_worktree.add_test_project("libhello")
    doc_builder = qidoc.builder.DocBuilder(doc_worktree, "libhello")
    doc_builder.configure()
    doc_builder.build()
    hello_index = libhello_proj.index_html
    link = find_link(hello_index, "world()")
    assert os.path.exists(link)
    doc_builder.install(tmpdir.strpath)
    link = find_link(tmpdir.join("index.html").strpath, "world()")
    assert not os.path.isabs(link)
    assert tmpdir.join(link).check(file=True)


def test_build(doc_worktree):
    """ Test Build """
    doc_worktree.add_test_project("libqi")
    qi_dox = doc_worktree.get_doc_project("qi-api", raises=True)
    qi_dox.configure()
    qi_dox.build()
    assert os.path.exists(qi_dox.index_html)
