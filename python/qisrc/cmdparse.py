def guess_current_project(worktree, cwd):
    """ Guess the current project using a worktree and the
    current working directory

    """


def project_from_arg(worktree, arg):
    """

        First assume that arg is an abs path
        (so that `qisrc sync ../bar/foo/` works)
        Then try assuming that arg in a name\
        (so that `qisrc sync bar\foo` also works
    """


def project_from_args(args):
    """

        Return a list of projects to use.

        * --work-tree given:
            no magic
        * work-tree not given:

          * if at the root of a worktree:
              * return every project

          * if in a subdirectory of a a project:
            * return the current project

         * raise an exception
    """
