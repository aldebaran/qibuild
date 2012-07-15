.. _qisrc-man-page:

qisrc man page
==============

SYNOPSIS
--------
**qisrc** <*COMMAND*> ...


DESCRIPTION
-----------

Provides actions to work with several sources.
Right now only ``git`` is supported

COMMANDS
--------


Useful commands:

pull
  Run ``git pull`` on every project

foreach -- *COMMAND* *COMMAND ARGS*
  Run the COMMAND on each project

add *URL*
  Get the project sources from the given URL and add it to the
  work tree

fetch *MANIFEST*
  Fetch all the project sources using a manifest URL

The manifest file should look like::

  <manifest>
    <project
      name="foo"
      url="git@git.example.com:foo.git"
    />
    <project
      name="bar"
      url="git@git.example.com:bar.git"
    />
  </manifest>
