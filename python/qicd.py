## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import argparse
import sys
import os
import difflib

import qisys.parsers
import qisys.worktree
import qibuild.worktree

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

    parser = argparse.ArgumentParser()
    parser.add_argument("token", nargs="?")
    parser.add_argument("-b", dest="build_name")
    args = parser.parse_args()
    path = None
    if args.build_name:
        try:
            path = get_qibuild_path(worktree, args.build_name)
        except qisys.worktree.NoSuchProject as e:
            sys.exit(str(e))
    else:
        token = sys.argv[1]
        path = find_best_match(worktree, token)
    if path:
        print(qisys.sh.to_posix_path(path))
        sys.exit(0)
    else:
        sys.stderr.write("no match for %s\n" % token)
        sys.exit(1)

def get_qibuild_path(worktree, name):
    """ Get the path of a qibuild project given its name """
    build_worktree = qibuild.worktree.BuildWorkTree(worktree)
    proj = build_worktree.get_build_project(name, raises=True)
    return proj.path

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
