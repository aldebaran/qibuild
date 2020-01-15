#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Stores configuration for git projects in a worktree
Delegates most of the work to :py:mod:`qisrc.git`` and
:py:mod:`qisrc.review`
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import re
import os

import qisrc.git
import qisrc.review
import qisys.qixml


class Remote(object):
    """ Remote Class """

    def __init__(self):
        """ Remote Init """
        self.url = ""
        self.name = None
        self.review = False
        self.default = False
        self.default_branch = "master"
        # used when joining the remote with a project name
        self.prefix = None
        # used for gerrit setup
        self.protocol = None
        self.username = None
        self.server = None
        self.port = None

    def _match_full_url(self, match):
        """ Match Full Url """
        self.protocol = "ssh"
        groupdict = match.groupdict()
        self.server = groupdict["server"]
        port = groupdict.get("port")
        if port:
            self.port = int(port)
        username = groupdict.get("username")
        if username:
            self.username = username
        else:
            username = qisrc.review.get_gerrit_username(self.server,
                                                        ssh_port=self.port)
            if not username:
                raise Exception("Could not guess ssh username")
            self.username = username
        prefix = "ssh://%s@%s" % (username, self.server)
        if self.port:
            prefix += ":%i" % self.port
        subfolder = groupdict.get("subfolder", "")
        prefix += subfolder
        if not prefix.endswith("/"):
            prefix += "/"
        self.prefix = prefix

    def _match_ssh_url(self, match):
        """ Match Ssh Url """
        groupdict = match.groupdict()
        self.protocol = "ssh"
        self.username = groupdict["username"]
        self.server = groupdict["server"]
        sep = groupdict["sep"] or ":"
        subfolder = groupdict.get("subfolder", "")
        self.prefix = "%s@%s%s%s" % (self.username, self.server, sep, subfolder)

    def _match_other_url(self, match):
        """ Match Other Url """
        groupdict = match.groupdict()
        self.protocol = groupdict["protocol"]
        if self.protocol == "file://":
            self.prefix = "foo"
        self.server = groupdict["server"]
        port = groupdict.get("port")
        if port:
            self.port = int(port)
        self.prefix = self.url
        if not self.prefix.endswith("/"):
            self.prefix += "/"

    def parse_url(self):
        """ Parse URL """
        if not self.url:
            raise Exception("Could not parse empty url as a git url")
        if self.url.startswith("file://"):
            prefix = self.url
            sep = "/"
            if os.name == 'nt' and "\\" in self.url:
                sep = "\\"
            if not prefix.endswith(sep):
                prefix += sep
            self.protocol = "file"
            self.prefix = prefix
            return
        full_ssh = re.compile(r"""
                        ssh://
                        ((?P<username>[^@]+)@)?
                        (?P<server>[^:/]+)
                        (:(?P<port>\d+))?
                        (?P<subfolder>.*)
                        """, re.VERBOSE)
        match = re.match(full_ssh, self.url)
        if match:
            self._match_full_url(match)
            return
        ssh_url = re.compile(r"""
                        (?P<username>.*?)
                        @
                        (?P<server>.*)
                        (?P<sep>[:/])?
                        (?P<subfolder>)
                        """, re.VERBOSE)
        match = re.match(ssh_url, self.url)
        if match:
            self._match_ssh_url(match)
            return
        other_url = re.compile(r"""
                        ((?P<protocol>(git|http|https))://)
                        (?P<server>[^:/]+)
                        (:(?P<port>\d+))?
                        """, re.VERBOSE)
        match = re.match(other_url, self.url)
        if match:
            self._match_other_url(match)
            return
        if os.path.exists(self.url):
            prefix = qisys.sh.to_native_path(self.url)
            prefix += os.path.sep
            self.prefix = prefix
        if not self.prefix:
            raise Exception("Could not parse %s as a git url" % self.url)

    def __repr__(self):
        """ String Representation """
        res = "<Remote %s: %s" % (self.name, self.url)
        if self.review:
            res += " (review)"
        res += ">"
        return res

    def __eq__(self, other):
        """ Return True is other is equal to self """
        return self.name == other.name and \
            self.url == other.url and \
            self.review is other.review and \
            self.default is other.default

    def __ne__(self, other):
        """ Return True is other is not equal to self """
        return not self.__eq__(other)


class Branch(object):
    """ Branch Class """

    def __init__(self):
        """ Branch Init """
        self.name = None
        self.tracks = None
        self.remote_branch = None
        self.default = False

    def __repr__(self):
        """ String Representation """
        return "<Branch %s (tracks: %s)>" % (self.name, self.tracks)

    def __eq__(self, other):
        """ Return True is other is equal to self """
        return self.name == other.name and \
            self.tracks == other.tracks and \
            self.remote_branch == self.remote_branch and \
            self.default is self.default

    def __ne__(self, other):
        """ Return True is other is not equal to self """
        return not self.__eq__(other)


class RemoteParser(qisys.qixml.XMLParser):
    """ RemoteParser Class """

    def __init__(self, target):
        """ RemoteParser Init """
        super(RemoteParser, self).__init__(target)
        self._required = ["name"]
        self._ignore = ["prefix", "protocol", "username", "server", "port"]


class BranchParser(qisys.qixml.XMLParser):
    """ BranchParserClass """

    def __init__(self, target):
        """ BranchParser Init """
        super(BranchParser, self).__init__(target)
        self._required = ["name"]
