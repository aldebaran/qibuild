#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import spam
import foo.bar.baz


def main():
    """ Main Entry Point """
    foo.bar.baz.baz()
    spam.spam()


if __name__ == "__main__":
    main()
