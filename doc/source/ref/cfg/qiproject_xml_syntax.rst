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
      names="spam"
    />
  </project>


The ``project`` name accepts a ``depends`` child.


depends node
------------

The list of dependencies is given as a white space separated
name list in a ``names`` attribute (note the plural form).


The names can be other projects in the same work tree, or the
name of packages in a toolchain.

The dependencies can be of two sorts:

  * **buildtime**: a dependency that is used when compiling the package

  * **runtime**: a dependency that is required when running the executables
    of the package, used when installing the package.

You can mix them using the ``buildtime="true"`` and ``runtime="true"``
attributes:

For instance

.. code-block:: xml

  <project name="hello">
    <depends buildtime="true" runtime="true"
      names="foo bar"
    />
    <depends runtime="true"
      names="spam"
    />
  </project>


Here runtime dependencies are ``foo,`` ``bar`` and ``spam``, and buildtime dependencies are just
``foo`` and ``bar``.
