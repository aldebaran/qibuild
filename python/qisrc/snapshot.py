#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Functions to generate and load snapshot. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import json
import collections

import qisrc.git
import qisrc.sync
import qisrc.status
import qisrc.reset
from qisys import ui


class Snapshot(object):
    """ Just a container for a git worktree snapshot """

    def __init__(self):
        """ Snapshot Init """
        self.refs = collections.OrderedDict()
        self.manifest = qisrc.sync.LocalManifest()
        self.format_version = None

    def dump(self, output_path, deprecated_format=True):
        """ Dump the snapshot into a human readable file """
        if deprecated_format:
            self._dump_deprecated(output_path)
        else:
            self._dump_json(output_path)

    def _dump_deprecated(self, output_path):
        """ Dump Deprecated """
        srcs = self.refs.keys()
        with open(output_path, 'w') as fp:
            for src in srcs:
                fp.write(src + ":" + self.refs[src] + "\n")

    def _dump_json(self, output_path):
        """ Dump JSON """
        with open(output_path, "w") as fp:
            serializable_manifest = dict()
            serializable_manifest["url"] = self.manifest.url
            serializable_manifest["branch"] = self.manifest.branch
            serializable_manifest["groups"] = self.manifest.groups
            if self.manifest.ref:
                serializable_manifest["ref"] = self.manifest.ref
            to_dump = {
                "format": 2,
                "manifest": serializable_manifest,
                "refs": self.refs
            }
            json.dump(to_dump, fp, indent=2)

    def load(self, source):
        """ Load a snapshot from a file path or a file object """
        # Try to open, else assume it's a file object
        try:
            fp = open(source, "r")
            data = fp.read()
        except TypeError:
            data = source.read()
        try:
            parsed = json.loads(data)
            self._load_json(parsed)
        except ValueError:
            self._load_deprecated(data)
        try:
            source.close()
        except AttributeError:
            pass

    def _load_deprecated(self, source):
        """ Load Deprecated """
        for line in source.splitlines():
            try:
                (src, sha1) = line.split(":")
            except ValueError:
                ui.error("could not parse", line)
                continue
            src = src.strip()
            sha1 = sha1.strip()
            self.refs[src] = sha1

    def _load_json(self, parsed_json):
        """ Load JSON """
        self.format_version = parsed_json["format"]
        if self.format_version == 1:
            manifest_json = parsed_json["manifests"]["default"]
        elif self.format_version == 2:
            manifest_json = parsed_json["manifest"]
        else:
            raise Exception("unknown format: %s" % self.format_version)
        self.refs = parsed_json["refs"]
        for key, value in manifest_json.items():
            setattr(self.manifest, key, value)

    def __eq__(self, other):
        """ Return True if other is equal to self """
        if not isinstance(other, Snapshot):
            return False
        return other.refs == self.refs and other.manifest == self.manifest

    def __ne__(self, other):
        """ Return True if other is not equal to self """
        return not self.__eq__(other)


def generate_snapshot(git_worktree, output_path, deprecated_format=True):
    """ Generate Snapshot """
    snapshot = git_worktree.snapshot()
    ui.info(ui.green, "Snapshot generated in", ui.white, output_path)
    return snapshot.dump(output_path, deprecated_format=deprecated_format)


def load_snapshot(git_worktree, input_path):
    """ Load a snapshot file and reset projects. """
    snapshot = Snapshot()
    ui.info(ui.green, "Loading snapshot from", ui.white, input_path)
    snapshot.load(input_path)
    for (src, ref) in snapshot.refs.items():
        ui.info("Loading", src)
        git_project = git_worktree.get_git_project(src, raises=False)
        if git_project:
            qisrc.reset.clever_reset_ref(git_project, ref)
