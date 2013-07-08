qisrc
=====

------------------------------------
Managing several git projects
------------------------------------

:Manual section: 1

SYNOPSIS
--------
**qisrc** <*COMMAND*> ...


DESCRIPTION
-----------

Provides actions to work with several sources.
Right now only ``git`` is supported

COMMANDS
--------

Commands:

add [--src ...] [[--branch|-b] ...] [URL|PATH]
  Add a new project to a worktree.

foreach -- *COMMAND* *COMMAND ARGS*
  Run the same command on each source project.

grep [pattern] [-- git grep options]
  Run git grep on every project.

init [[--branch|-b] ...] [[--profile|-p] ...] [--force|-f] [--no-review] MANIFEST_URL [MANIFEST_NAME]
  Init a new qisrc workspace.

list [PATTERN]
  List the names and paths of every project, or those matching a pattern.

push [--no-review] [-n|--dry-run] [[--cc|--reviewers] ...]
  Push changes for review.

remove [--from-disk] [SRC]
  Remove a project from a worktree.

status [-u|--untracked-files] [-b|--show-branch]
  List the state of all git repositories and exit.

sync [--no-review]
  Synchronize the given worktree with its manifests.
