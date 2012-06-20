.. _qitoolchain-man-page:

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

init NAME [FEED_URL]
  create a new toolchain

update NAME
  update a toolchain using the last feed

add-package -c TOOLCHAIN_NAME PACKAGE_NAME PACKAGE_PATH
  add a new package to the given toolchain

import-package -c TOOLCHAIN_NAME [PACKAGE_NAME] PACKAGE_PATH
  import a binary package into the given toolchain

  Current supported binary package formats:

  * Gentoo

remove-package -c TOOLCHAIN_NAME PACKAGE_NAME
  remove the package from the toolcain


Note: to use a toolchain, you must pass the ``-c`` option to your
``qibuild`` action, or set a default toolchain in the
configuration file of you worktree (``QI_WORK_TREE/.qi/qibuild.xml``)
like this:

.. code-block:: ini

  <qibuild version="1">
    <defaults config=NAME />
  </qibuild>

Note: the ``import-package`` action may take benefit from *portage*
(see: http://www.gentoo.org/proj/en/portage/index.xml) if it is found on your
system.
