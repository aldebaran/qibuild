#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Abstract Builder Interface """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import abc


class AbstractBuilder(object):
    """
    AbstractBuilder.
    The interface of a builder.
    A builder can build multiples projects at once.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        """ AbstractBuilder Init """
        self.name = name

    @abc.abstractmethod
    def configure(self, *args, **kwargs):
        """ Configure """
        raise NotImplementedError

    @abc.abstractmethod
    def build(self, *args, **kwargs):
        """ Build """
        raise NotImplementedError

    @abc.abstractmethod
    def install(self, dest, *args, **kwargs):
        """ Install """
        raise NotImplementedError
