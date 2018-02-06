# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
from __future__ import print_function

import sys
import os
import difflib

import qisys.parsers


def main():
    """ Main entry point """
    try:
        worktree = qisys.parsers.get_worktree({})
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(2)
    if len(sys.argv) < 2:
        print(worktree.root)
        sys.exit(0)

    token = sys.argv[1]
    path = find_best_match(worktree, token)
    if path:
        print(path)
        sys.exit(0)
    else:
        sys.stderr.write("no match for %s\n" % token)
        sys.exit(1)


def find_best_match(worktree, token):
    """ Find the best match for a project in a worktree

    """
    candidates = list()
    for project in worktree.projects:
        to_match = os.path.basename(project.src)
        if token in to_match:
            candidates.append(project)
    max_score = 0
    best_project = None
    for candidate in candidates:
        to_match = os.path.basename(candidate.src)
        sequence_matcher = difflib.SequenceMatcher(a=token, b=to_match)
        score = sequence_matcher.ratio()
        if score > max_score:
            max_score = score
            best_project = candidate
    if best_project:
        return best_project.path


if __name__ == "__main__":
    main()
