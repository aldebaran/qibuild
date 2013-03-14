.. _qiproject-xml-syntax:

qiproject.xml syntax
====================

General
-------


The ``qiproject.xml`` file should always be at the top of a
project registered in a :term:`worktree`

It can optionally contains paths to subfolders, so
that you can have nested projects.


.. code-block:: xml

  <project>
    <project src="subfolder" />
  </project>



This is the basis for every qiBuild tool.

Each tool then parses the same file using its associated tags,
ignoring the rest.

This helps having loosing coupled dependencies between the various tools.


qibuild
--------

There can only be one qibuild project per source.

The ``CMakeLists.txt`` must be next to the ``qiproject.xml``

The ``qiproject.xml`` must contain a ``qibuild`` element.

The ``qibuild`` element must contain a ``name`` attribute.

The name of the project must be unique in the worktree.

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

  <project >
    <qibuild name="hello">
      <depends buildtime="true" runtime="true" names="foo bar" />
      <depends runtime="true" names="spam" />
    </qibuild>
  </project>


Here runtime dependencies are ``foo,`` ``bar`` and ``spam``, and buildtime dependencies are just
``foo`` and ``bar``.

qilinguist
----------

This is the configuration for adding translations to your source code.
This configuration is used by ``qilinguist`` to generate translation files
and install rules.


The file will look like:

.. code-block:: xml

  <project>
    <translate domain="hello" linguas="fr_FR en_US" tr="gettext" />
  </project>

Tags definitions:

* **domain**: The name of the generated dictionary.
* **linguas**: A list of all locales supported.
* **tr**: Defined if you use gettext or QT internationalization (value can be:
  "gettext" or "qt").
