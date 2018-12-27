#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Toolchain Feeds """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
from xml.etree import ElementTree
import six

import qitoolchain
import qisrc.git
import qisys
import qisys.archive
import qisys.remote
import qisys.version
from qisys import ui

if six.PY3:
    from urllib import parse as urlparse
else:
    import urlparse


def is_url(location):
    """ Check that a given location is an URL """
    return location and "://" in location


def raise_parse_error(package_tree, feed, message):
    """ Raise a nice parsing error about the given package_tree element. """
    as_str = ElementTree.tostring(package_tree)
    mess = "Error when parsing feed: '%s'\n" % feed
    mess += "Could not parse:\t%s\n" % as_str
    mess += message
    raise Exception(mess)


def tree_from_feed(feed_location, branch=None, name=None):
    """ Returns an ElementTree object from an feed location """
    fp = None
    tree = None
    try:
        if feed_location and os.path.exists(feed_location):
            fp = open(feed_location, "r")
        elif is_url(feed_location):
            fp = qisys.remote.open_remote_location(feed_location)
        else:
            raise Exception("Could not parse %s: Feed location is not an existing path nor an url" % feed_location)
        tree = ElementTree.ElementTree()
        tree.parse(fp)
    except Exception as e:
        ui.error(e.message)
        raise
    finally:
        if fp:
            fp.close()
    return tree


def open_git_feed(toolchain_name, feed_url, name=None, branch="master", first_pass=True):
    """ Open a Git Feed """
    git_path = qisys.sh.get_share_path("qi", "toolchains", toolchain_name + ".git")
    git = qisrc.git.Git(git_path)
    if first_pass:
        if os.path.exists(git_path):
            git.call("remote", "set-url", "origin", feed_url)
            git.call("remote", "update", "--prune", "origin")
            git.call("fetch", "origin", "--quiet")
            git.call("reset", "--hard", "--quiet", "origin/%s" % branch)
        else:
            git.clone(feed_url, "--quiet", "--branch", branch)
        feed_path = os.path.join(git_path, "feeds", name + ".xml")
    else:
        feed_path = feed_url
    return feed_path


class ToolchainFeedParser(object):
    """ A class to handle feed parsing """

    def __init__(self, name):
        """ ToolchainFeedParser Init """
        self.name = name
        self.packages = list()
        # A list of packages to be blacklisted
        self.blacklist = list()
        # A dict name -> version used to only keep the latest
        # version
        self._versions = dict()

    def get_packages(self):
        """ Get the parsed packages """
        res = [x for x in self.packages if x.name not in self.blacklist]
        return res

    def append_package(self, package_tree):
        """
        Add a package to self.packages.
        If an older version of the package exists, replace by the new version
        """
        version = package_tree.get("version")
        name = package_tree.get("name")
        names = self._versions.keys()
        if name not in names:
            self._versions[name] = version
            self.packages.append(qitoolchain.qipackage.from_xml(package_tree))
        else:
            if version is None:
                # if version not defined, don't keep it
                return
            prev_version = self._versions[name]
            if prev_version and qisys.version.compare(prev_version, version) > 0:
                return
            else:
                self.packages = [x for x in self.packages if x.name != name]
                self.packages.append(qitoolchain.qipackage.from_xml(package_tree))
                self._versions[name] = version

    def parse(self, feed, branch=None, name=None, first_pass=True):
        """ Recursively parse the feed, filling the self.packages """
        tc_path = qisys.sh.get_share_path("qi", "toolchains", self.name)
        if branch and name:
            feed = open_git_feed(self.name, feed, branch=branch, name=name, first_pass=first_pass)
        tree = tree_from_feed(feed)
        package_trees = tree.findall("package")
        package_trees.extend(tree.findall("svn_package"))
        for package_tree in package_trees:
            package_tree.set("feed", feed)
            self.append_package(package_tree)
            subpkg_trees = package_tree.findall("package")
            for subpkg_tree in subpkg_trees:
                subpkg_tree.set("feed", feed)
                subpkg_tree.set("directory",
                                os.path.join(tc_path, package_tree.get("name")))
                subpkg_tree.set("subpkg", "1")
                self.append_package(subpkg_tree)
        feeds = tree.findall("feed")
        for feed_tree in feeds:
            # feed_name = feed_tree.get("name")
            feed_url = feed_tree.get("url")
            feed_path = feed_tree.get("path")
            assert feed_path or feed_url, "Either 'url' or 'path' attributes must be set in a 'feed' non-root element"
            # feed_url can be relative to feed:
            if feed_path and branch:
                feed_path = os.path.join(tc_path + ".git", feed_tree.get("path"))
                self.parse(feed_path)
            elif feed_url:
                if not is_url(feed_url):
                    feed_url = urlparse.urljoin(feed, feed_url)
                self.parse(feed_url)
        select_tree = tree.find("select")
        if select_tree is not None:
            blacklist_trees = select_tree.findall("blacklist")
            for blacklist_tree in blacklist_trees:
                name = blacklist_tree.get("name")
                if name:
                    self.blacklist.append(name)
