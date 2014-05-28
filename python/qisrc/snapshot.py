## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Functions to generate and load snapshot."""

import collections
import json

from qisys import ui

import qisrc.git
import qisrc.status
import qisrc.reset


class Snapshot(object):
    """ Just a container for a git worktree snapshot """
    def __init__(self):
        self.refs = collections.OrderedDict()
        self.manifests = dict()
        self.format_version = None

    def dump(self, output_path, deprecated_format=True):
        """ Dump the snapshot into a human readable file """
        if deprecated_format:
            self._dump_deprecated(output_path)
        else:
            self._dump_json(output_path)

    def _dump_deprecated(self, output_path):
        srcs = self.refs.keys()
        with open(output_path, 'w') as fp:
            for src in srcs:
                fp.write(src + ":" + self.refs[src] + "\n")

    def _dump_json(self, output_path):
        with open(output_path, "w") as fp:
            # Json does not know about classes, so
            # we are going to cheat a little
            serializable_manifests = dict()
            for key, value in self.manifests.iteritems():
                serializable_manifests[key] = vars(value)
            to_dump = {
                    "format" : 1,
                    "manifests" : serializable_manifests,
                    "refs" : self.refs
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
        self.format_version = parsed_json["format"]
        self.refs = parsed_json["refs"]
        self.format_version = None
        self.manifests = dict()
        for manifest_name, manifest_json in parsed_json["manifests"].iteritems():
            manifest = qisrc.sync.LocalManifest()
            self.manifests[manifest_name] = manifest
            for key, value in manifest_json.iteritems():
                setattr(manifest, key, value)

    def __eq__(self, other):
        if not isinstance(other, Snapshot):
            return False
        return other.refs == self.refs and other.manifests == self.manifests

    def __ne__(self, other):
        return not self.__eq__(other)

def generate_snapshot(git_worktree, output_path, deprecated_format=True):
    snapshot = git_worktree.snapshot()
    return snapshot.dump(output_path, deprecated_format=deprecated_format)
    ui.info(ui.green, "Snapshot generated in", ui.white, output_path)

def load_snapshot(git_worktree, input_path):
    """Load a snapshot file and reset projects."""
    snapshot = Snapshot()
    ui.info(ui.green, "Loading snapshot from", ui.white,  input_path)
    snapshot.load(input_path)
    for (src, ref) in snapshot.refs.iteritems():
        ui.info("Loading", src)
        git_project = git_worktree.get_git_project(src, raises=False)
        if git_project:
            qisrc.reset.clever_reset_ref(git_project, ref)
