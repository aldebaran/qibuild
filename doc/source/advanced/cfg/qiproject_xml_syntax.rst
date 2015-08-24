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

  <project version="3" />
    <project src="subfolder" />
  </project>


This is the basis for every qiBuild tool.
(Note that the ``version=3`` is not the project version,
it's just that the syntax was introduced in qibuild 3.0)

Each tool then parses the same file using its associated tags,
ignoring the rest.

This helps having loosely coupled dependencies between the various tools.

The ``qiproject`.xml`` should contain the list of maintainers, like so

.. code-block:: xml

  <project version="3">
    <maintainer email="jdoe@company.com">John Doe</maintainer>
  </project>

If the project is no longer maintained, specify it like so:

.. code-block:: xml

  <project version="3">
    <maintainer>ORPHANED</maintainer>
  </project>


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

The dependencies can be of four sorts:

* **buildtime**: a dependency that is required when using the package for compiling,
  used when installing the project and generating re-distributable packages

* **runtime**: a dependency that is required when running the executables
  of the package, used when installing the package.

* **testtime**: a dependency that is required for testing the package

* **host**: a dependency containing host tools. See :ref:`qibuild-host-tools`

You can mix them using the ``buildtime="true"`` and ``runtime="true"``
attributes:

For instance

.. code-block:: xml

  <project version="3" >
    <qibuild name="hello">
      <depends buildtime="true" runtime="true" names="foo bar" />
      <depends runtime="true" names="spam" />
      <depends host="true" names="eggs" />
    </qibuild>
  </project>


Here runtime dependencies are ``foo,`` ``bar`` and ``spam``, and buildtime
dependencies are just ``foo`` and ``bar``.
There is a host dependency on ``eggs``.

qilinguist
----------

This is the configuration for adding translations to your source code.
This configuration is used by ``qilinguist`` to generate translation files
and install rules.


The file will look like:

.. code-block:: xml

  <project version="3" >
    <qilinguist name="hello" linguas="fr_FR en_US" tr="gettext" />
  </project>

Tags definitions:

* **name**: The name of the generated dictionary.
* **linguas**: A list of all locales supported.
* **tr**: Defined if you use ``gettext`` or ``Qt Linguist``
  internationalization (value can be: ``gettext`` or ``qt``).

qipy
----

This is used to configure Python projects.

Assuming you have a layout looking like:

.. code-block:: console


    foobarspam
      qiproject.xml
      lib
        bar.py
        foo
           __init__.py
      bin
        eggs

Here is what the ``qiproject.xml`` should look like:

.. code-block:: xml

  <project version="3">
    <qipython name="foobarspam">
      <module name="bar" src="lib" />
      <package name="foo" src="lib" />
      <script name="eggs" src="bin/eggs" />
    </qipython>
  </projct>

Note that you can also write a ``setup.py`` file.
In this case, specify ``<setup with_distutils="true">`` in the
``qiproject.xml``.

.. code-block:: xml

  <project  version="3">
    <qipython name="foobarspam">
      <setup with_distutils="true" />
    </qipython>
  </project>


qidoc
------

This is used by ``qidoc``

Doc projects can be of three type ``sphinx``,
``doxygen`` or ``template``.

Here is what the ``qiproject.xml`` looks like for each type.

.. code-block:: xml

  <project version="3">
    <!-- for sphinx projects -->
    <qidoc name="foo" type="sphinx" dest="lib/foo" />
    <!-- for doxygen projects -->
    <qidoc name="bar" type="doxygen" dest="lib/bar" />
    <!-- for template project -->
    <qidoc type="template"/>
  </project>

There should be zero or one ``template`` by worktree.

Names of ``sphinx`` and ``doxygen`` projects should be unique.

A project can have a list of dependencies, which is specified in
a ``depends`` tag, like this:

.. code-block:: xml

  <qidoc type="sphinx" name="hello">
    <depends name="world" />
  </qidoc>

Doc projects can have a ``dest`` attribute. For instance, assuming
that ``world`` is a dependency of ``hello``, and you have the
following ``qiproject.xml`` files:

.. code-block:: xml

  <!-- in hello/qiproject.xml -->
  <project version="3">
    <qidoc type="sphinx" name="hello">
      <depends name="world" />
    </qidoc>
  </project>

.. code-block:: xml

  <!-- in world/qiproject.xml -->
  <project version="3">
    <qidoc type="sphinx" name="world" dest="lib/world" />
  </project>

Then when building ``hello`` documentation, ``world`` documentation
will be built, and put in a ``lib/world`` subfolder.

You can also specify a Python script to be run before building anything:

.. code-block:: xml

  <project version="3">
    <qidoc type="sphinx" name="hello">
      <prebuild script="gen_rst.py" />
    </qidoc>
  </project>

Lastly, you can specify examples for Sphinx projects.
For each example, the ``src`` folder will
be zipped and made available as a ``..download`` directive:

.. code-block:: console

  hello
    index.rst
    samples
      foo
        foo.cpp
        CMakeLists.txt
      bar
        bar.py
        setup.py

.. code-block:: xml

  <project version="3">
    <qidoc type="sphinx" name="hello">
      <examples>
        <example src="samples/foo" />
        <example src="samples/bar" />
      </examples>
    </qidoc>

.. code-block:: rst

    .. In index.rst

    Download the full sources of the ``foo`` example:
    :download:`foo.zip <../foo.zip>`
