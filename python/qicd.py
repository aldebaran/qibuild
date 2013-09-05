import sys
import os
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
    matches = list()
    for project in worktree.projects:
        if "/" in token:
            to_match = project.src
        else:
            to_match = os.path.basename(project.src)
        if token in to_match:
            matches.append(project.path)

    matches.sort(key=len)
    if not matches:
        return None
    return matches[0]

if __name__ == "__main__":
    main()
