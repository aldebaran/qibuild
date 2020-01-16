#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import gettext

name = "hello"
this_dir = os.path.dirname(__file__)
this_dir = os.path.abspath(this_dir)
this_po_dir = os.path.join(this_dir, "po")
candidates = [this_po_dir, sys.prefix]
path = None
for candidate in candidates:
    expected = os.path.join(candidate, "share", "locale", name)
    print("trying", expected)
    if os.path.exists(expected):
        path = expected
        break
if path is None:
    print("Could not find translations path")
gettext.bindtextdomain(name, path)
gettext.textdomain(name)


def main():
    """ Main Entry Point """
    print(gettext.gettext("hello, world"))


if __name__ == "__main__":
    main()
