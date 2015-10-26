qitoolchain
===========

------------------------------------
Managing pre-compiled binaries
------------------------------------

:Manual section: 1

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

init NAME [FEED_URL]
  create a new toolchain

update NAME
  update a toolchain using the last feed

convert-package [NAME] PACKAGE_PATH
  turn a package (binary archive or install directory) into a qiBuild package

  Current supported binary package formats:

  * Gentoo

add-package -t TOOLCHAIN_NAME PACKAGE_PATH
  add a new qiBuild package to the given toolchain

import-package -t TOOLCHAIN_NAME --name PACKAGE_NAME PACKAGE_PATH
  import a package (binary archive or install directory) into a qiBuild package

  Convert the binary package to a qiBuild package and automatically
  add it to the toochain.

  Current supported binary package formats:

  * Gentoo

remove-package -t TOOLCHAIN_NAME PACKAGE_NAME
  remove the package from the toolcain


NOTES
-----

.. note:: to use a toolchain, you must first create a build config with
  ``qibuild add-config NAME --toolchain TOOLCHAIN_NAME`` and then
  pass the ``-c`` option to your ``qibuild`` action.

  You can also set a default build configuration with ``qibuild set-default``.

.. note:: the ``import-package`` action may take benefit from *portage*
   (see: http://www.gentoo.org/proj/en/portage/index.xml) if it is found on your
   system.
