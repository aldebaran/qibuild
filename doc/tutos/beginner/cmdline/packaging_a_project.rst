Packaging a project
===================

You may want to distribute a pre-compiled package for an other person to use.
With QiBuild, this is easy.

Runtime package
---------------

Simply run::

  qibuild package foo

This will configure, build and install the foo project in
QI_WORK_TREE/package/foo, and  and generate a re-distributable binary package
in QI_WORK_TREE/package/foo.tar.gz) (or foo.zip if you are on windows)

The archive will by default contain only the runtime components (executables,
dependent libraries, data ...)

Development package
-------------------

If you want to provide a pre-compiled package so that other people can compile
their own software with it, run::

  qibuild package --devel foo

The archive will contain the static libraries, the headers (provided
you used the correct install rule), the cmake files, and so on.
Notes: depedencies will not be installed inside the devel package, because
this package is supposed to be use inside a toolchain.

More on this in the :ref:`using-toolchains` tutorial.

