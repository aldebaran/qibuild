""" Handling exception inside qBuild"""

class Error(Exception):
    """ Base class for all qibuild exceptions.

    When an exception is raised that is not a daughter
    of this class, assume it's a crash and generate a
    bug report

    Alternatively, if you are in an action,
    you can use:

        ui.fatal("message")

    or simply:

        sys.exit(2)

    """
    pass
