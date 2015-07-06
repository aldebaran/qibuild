.. _qibuild-packaging-project:

Packaging a project
===================

You may want to distribute a pre-compiled package for an other person to use.
With qiBuild, this is easy.

Runtime package
---------------

Simply run:

.. code-block:: console

  $ qibuild install --runtime foo /path/to/dest

This installs the ``foo`` project in ``/path/to/dest``

The destination folder will by default contain only the runtime components (executables,
dependent libraries, data ...)

You can then zip the destination folder to get a redistributable binary.

Development package
-------------------

If you want to provide a pre-compiled package so that other people can compile
their own software with it, run:

.. code-block:: console

  $ qibuild package foo

The archive will contain the static libraries, the headers (provided
you used the correct install rule), the CMake files, and so on.

Notes: dependencies will not be installed inside the devel package, because
this package is supposed to be used inside a toolchain.

More on this in the :ref:`using-toolchains` tutorial.
