.. _qibuild-man-page:

qibuild man page
================


SYNOPSIS
--------
**qibuild** <*COMMAND*> ...


DESCRIPTION
-----------

Provides several actions to work with projects.
You can configure, build, install and generate binary archives of projects.


COMMANDS
--------

Useful commands:

(use ``qibuild --help`` to have the full list of available actions)

init:
  Should be run in a empty directory. Create a new work tree.


create PROJECT
  Create a new project in the work tree.

  In the following actions, you do not need to specify the project name if you
  are in a subdirectory of this project

configure [PROJECT]
  Configure a project.

make [PROJECT]
  Build a project

test [PROJECT]
  Run the project tests

install PROJECT DESTINATION
  Install PROJECT to the DESTINATION

package PROJECT
  Generate a pre-compiled archive of the project.
  Archive will be generated in ``WORK_TREE/package/``


OPTIONS
-------

Useful options:

(use ``qibuild COMMAND --help`` to have the full list of available options
for the given COMMAND)

--work-tree ['WORK_TREE']
    Specify the work tree.

-h, --help ['TOPIC']
    Print help about TOPIC.

-v, --verbose
    Set verbose output

--backtrace
    Print the full backtrace when an error occurs. (useful for bug reports)


Useful build options:

--release
  Build in release (by default, qibuild builds in debug)


CONFIGURATION
-------------

Configuration is done in ``.qi/qibuild.cfg`` or in ``.config/.qi/qibuild.cfg``.


EXIT STATUS
-----------

0
    Success

2
    Failure

