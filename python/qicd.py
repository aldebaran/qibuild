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
    project_scores = dict()
    for project in worktree.projects:
        if "/" in token:
            to_match = project.src
        else:
            to_match = os.path.basename(project.src)
        sequence_matcher = difflib.SequenceMatcher(a=token, b=to_match)
        project_scores[project] = sequence_matcher.ratio()

    max_score = 0
    best_project = None
    for project, score in project_scores.iteritems():
        if score > max_score:
            best_project = project
            max_score = score
    if best_project:
        return best_project.path


if __name__ == "__main__":
    main()
