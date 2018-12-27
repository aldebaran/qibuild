#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """

import os
import sys


sys.path.insert(0, os.path.abspath('../tools'))
sys.path.insert(0, os.path.abspath('../../python'))

project = "qiBuild"
version = "3.12.1"
release = version
extensions.append("cmakedomain")
extensions.append("sphinx.ext.autodoc")
extensions.append("sphinxcontrib.spelling")

templates_path = ["../source/_templates"]

html_additional_pages = {
    'index': 'index.html'
}

autodoc_member_order = 'bysource'

exclude_patterns = ['man/*']

man_pages = [
    ('man/qisrc', 'qisrc', u'Handle several project sources',
     [u'Aldebaran Robotics'], 1),
    ('man/qibuild', 'qibuild', u'Configure, build, install, package your project',
     [u'Aldebaran Robotics'], 1),
    ('man/qitoolchain', 'qitoolchain', u'Hanlde sets of pre-compiled packges',
     [u'Aldebaran Robotics'], 1),
    ('man/qidoc', 'qidoc', u'Hanlde doxygen and sphinx projects',
     [u'Aldebaran Robotics'], 1),
    ('man/qilinguist', 'qilinguist', u'Translate projects using gettext or Qt linguist',
     [u'Aldebaran Robotics'], 1)
]

html_static_path = ['../source/_static']
