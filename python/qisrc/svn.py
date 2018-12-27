#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Fake Git """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import subprocess

import qisys.command
from qisys import ui


class Svn(object):
    """ Svn Class """

    def __init__(self, path):
        """ Svn Init """
        self.path = path

    def call(self, *args, **kwargs):
        """ Call """
        if "cwd" not in kwargs.keys():
            kwargs["cwd"] = self.path
        ui.debug("svn", " ".join(args), "in", kwargs["cwd"])
        if "quiet" not in kwargs.keys():
            kwargs["quiet"] = False
        svn = qisys.command.find_program("svn", raises=True)
        cmd = [svn]
        cmd.extend(args)
        raises = kwargs.get("raises")
        if raises is False:
            del kwargs["raises"]
            del kwargs["quiet"]
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       **kwargs)
            out = process.communicate()[0]
            # Don't want useless blank lines
            out = out.rstrip("\n")
            ui.debug("out:", out)
            return process.returncode, out
        else:
            if "raises" in kwargs:
                del kwargs["raises"]
            qisys.command.call(cmd, **kwargs)
        return None

    def commit_all(self, message):
        """ Commit All """
        __rc, out = self.call("status", raises=False)
        for line in out.splitlines():
            line = line.strip()
            filename = line[8:]
            if line.startswith("!"):
                self.call("remove", filename)
            if line.startswith("?"):
                self.call("add", filename)
            # Prevent 'Node has unexpectedly changed kind' error
            # when a file is replaced by a symlink.
            # see http://antoniolorusso.com/blog/2008/09/29/svn-entry-has-unexpectedly-changed-special-status/
            if line.startswith("~"):
                full_path = os.path.join(self.path, filename)
                if os.path.islink(full_path):
                    target = os.readlink(full_path)  # pylint:disable=no-member
                    os.remove(full_path)
                    self.call("remove", filename)
                    os.symlink(target, full_path)  # pylint:disable=no-member
                    self.call("add", filename)
                else:
                    ui.error("Could not deal with", filename, "\n",
                             "Please open a bug report")
        self.call("commit", "--message", message)
