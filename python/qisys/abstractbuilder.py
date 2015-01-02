## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Abstract Builder Interface """

import abc

class AbstractBuilder(object):
    __metaclass__ = abc.ABCMeta
    """ the interface of a builder
        a builder can build multiples projects at once
    """
    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def configure(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def build(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def install(self, dest, *args, **kwargs):
        raise NotImplementedError

