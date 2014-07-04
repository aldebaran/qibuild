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

    It's the shortest basename matching the token if there
    are no '/' in token, else, the shortest src matching the token

    """
    possibilities = [x.src for x in worktree.projects]
    matches = difflib.get_close_matches(token, possibilities, cutoff=0)
    if matches:
        closest_src =  matches[0]
        return worktree.get_project(closest_src).path
    return None


if __name__ == "__main__":
    main()
