qisrc
=====

-----------------------------
Managing several git projects
-----------------------------

:Manual section: 1

SYNOPSIS
--------
**qisrc** command

DESCRIPTION
------------

Provides several actions to work with multiple git projects

COMMANDS
--------

Useful commands:

init MANIFEST_URL:
  MANIFEST_URL should be a git URL containing a ``manifest.xml`` file
  Create a new worktree, reading the repositories to clone from the manifest.

sync:
  Fetch and apply remote changes to the git projects of the worktree

push:
  Push changes for review, or directly to the remote server if the project is
  not configured for code review
