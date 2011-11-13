.. _qibuild-manifest-syntax:

qibuild.manifest syntax
=======================

General
-------

There must be exactly one `qibuild.manifest` file per
project inside a `QI_WORK_TREE`.

Every `qibuild.manifest` must at least contains a section
`[project <name>]`

Known keys
----------

**depends**

  The list of build dependencies.
  For instance, with a ``world`` project in ``src/world`` and
  an hello project in ``src/hello``, you should have

.. code-block:: ini

    # in src/world/qibuild.manifest
    [project world]

.. code-block:: ini

    # in src/hello/qibuild.manifest
    [project hello]
    depends = world

The list of dependencies is given as a white space separated
name list.

The names can be other projects in the same work tree, or the
name of packages in a toolchain.


**rdepends**

  A list of runtime dependencies.

  The list of dependencies is given as a white space separated
  name list.

  The names can be other projects in the same work tree, or the
  name of packages in a toolchain.

  Those will used by the ``qibuild install --runtime`` command.
