#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiToolChain: Handle set of Precompiled Packages """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qitoolchain.toolchain import Toolchain
from qitoolchain.toolchain import get_tc_names


def get_toolchain(tc_name, raises=True):
    """ Get an existing tolchain using its name """
    tc_names = get_tc_names()
    if tc_name not in tc_names:
        mess = "No such toolchain: %s\n" % tc_name
        mess += "Known toolchains are:\n"
        for name in tc_names:
            mess += "  * " + name + "\n"
        if raises:
            raise Exception(mess)
        return None
    return Toolchain(tc_name)


def ensure_name_is_valid(tc_name):
    """ Validate the name has no unsupported characters """
    if tc_name:
        bad_chars = r'<>:"/\|?*'
        for bad_char in bad_chars:
            if bad_char in tc_name:
                mess = "Invalid toolchain name: '%s'\n" % tc_name
                mess += "A valid toolchain name should not contain any "
                mess += "of the following chars:\n"
                mess += " ".join(bad_chars)
                raise Exception(mess)
