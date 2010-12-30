#!/usr/bin/env python
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

class Toolchain:
    def __init__(self, name):
        if name == None:
            self.name = "system"
        else:
            self.name = name
        self.projects = list()

    def update(self, tob):
        self.projects = tob.configstore.get("toolchain", self.name, "provide", default=list())
