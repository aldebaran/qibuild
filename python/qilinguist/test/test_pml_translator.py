#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qilinguist.pml_translator import translations_files_from_pml


def test_parse_pml(tmpdir):
    """ Test Parse Pml """
    pml_path = tmpdir.join("foo.pml")
    pml_path.write("""
<Package name="foo" format_version="4">
  <Translations>
    <Translation name="foo_fr_FR"
                 src="translations/foo_fr_FR.ts"
                 language="fr_FR" />
    <Translation name="foo_en_US"
                 src="translations/foo_en_US.ts"
                 language="en_US" />
  </Translations>

</Package>
""")
    translations = translations_files_from_pml(pml_path.strpath)
    assert translations == ["translations/foo_fr_FR.ts",
                            "translations/foo_en_US.ts"]
