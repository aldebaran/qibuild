.. _qiproject-xml-syntax:

qiproject.xml syntax
====================

General
-------

There must be exactly one ``qiproject.xml`` file per
project inside a :term:`worktree`

Every ``qiproject.xml`` must have a root element named
``project`` with a ``name`` attribute.

The file will look like:

.. code-block:: xml

  <project name="hello">
    <depends buildtime="true" runtime="true"
      names="foo bar"
    />
    <depends runtime="true"
      name="spam"
    />
  </project>



project node
------------

The project nodes accepts a

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
