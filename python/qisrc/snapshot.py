## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Functions to generate and load snapshot."""

import collections

from qisys import ui

import qisrc.git
import qisrc.status


class Snapshot(object):
    """ Just a container for a git worktree snapshot """
    def __init__(self):
        self.sha1s = collections.OrderedDict()

    def dump(self, output_path):
        """ Dump the snapshot into a human readable file """
        srcs = self.sha1s.keys()
        with open(output_path, 'w') as fp:
            for src in srcs:
                fp.write(src + ":" + self.sha1s[src] + "\n")

    def load(self, input_file):
        """ Load a snapshot from a file path or a file object """
        # Try to open, else assume it's a file object
        try:
            fp = open(input_file, "r")
        except TypeError:
            fp = input_file
        for line in fp:
            (src, sha1) = line.split(":")
            src = src.strip()
            sha1 = sha1.strip()
            self.sha1s[src] = sha1
        try:
            fp.close()
        except AttributeError:
            pass

    def __eq__(self, other):
        if not isinstance(other, Snapshot):
            return False
        return other.sha1s == self.sha1s

    def __ne__(self, other):
        return not self.__eq__(other)

def generate_snapshot(git_worktree, output_path):
    """Generate a snapshot file."""
    snapshot = git_worktree.snapshot()
    snapshot.dump(output_path)
    ui.info(ui.green, "Snapshot generated in", ui.white, output_path)

def load_snapshot(git_worktree, input_path):
    """Load a snapshot file and reset projects."""
    snapshot = Snapshot()
    ui.info(ui.green, "Loading snapshot from", ui.white,  input_path)
    snapshot.load(input_path)
    failures = list()
    for (src, sha1) in snapshot.sha1s.iteritems():
        ui.info("Loading", src)
        git_project = git_worktree.get_git_project(src, raises=True)

        git = qisrc.git.Git(git_project.path)
        with git.transaction() as transaction:
            git.fetch("--all")
            git.reset("--hard", sha1)
        if not transaction.ok:
            failures.append(src)

    if failures:
        ui.warning("Loading failed for the following projects")
        for failure in failures:
            ui.warning(" * ", failure)
