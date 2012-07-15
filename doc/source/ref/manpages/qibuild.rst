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


All following command accept a ``-c,--config`` argument which should be
the name a a toolchain.
(see :ref:`qitoolchain-man-page`)

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
  Archive will be generated in ``QI_WORK_TREE/package/``


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

Configuration is done in ``~/.config/qi/qibuild.xml``.

See ``qibuild config --wizard``


EXIT STATUS
-----------

0
    Success

2
    Failure

