:orphan:

qitoolchain man page
====================

SYNOPSIS
--------
**qitoolchain** <*COMMAND*> ...

DESCRIPTION
-----------

Provides actions to work with a toolchain.
A toolchain is a set of pre-compiled binary packages, generated
for instance with ``qibuild package``


COMMANDS
--------

create NAME
  create a new toolchain

add -c TOOLCHAIN_NAME PACKAGE_NAME PACKAGE_PATH
  add a new package to the given toolchain

remove -c TOOLCHAIN_NAME PACKAGE_NAME
  remove the package from the toolcain


Note: to use a toolchain, you must pass the ``-c`` option to your
``qibuild`` action, or set a default toolchain in the configuration, like
this::

  [general]
  config = NAME


