.. _qibuild-writing-documentation:

Writing qiBuild documentation
=============================

One of the strengths of the qiBuild framework is the documentation
you are reading right now ;)

It is completely written using `sphinx <http://sphinx.pocoo.org/>`_,
so do not hesitate to create links between various sections.

Please submit documentation updates (if relevant) when you submit your patches.

Documenting CMake API
----------------------

The :ref:`qibuild-cmake-api` is automatically generated from the
comments of the cmake files in ``cmake/qibuild``

If you add a new file, please add it to the list in ``ref/cmake/api.rst``

Also, when changing the comments of a cmake functions, please
regenerate the ``.rst`` files to check the output.

You can do so by running ``make`` in ``doc/``, or using:

.. code-block:: console

  $ cd doc
  $ python tools/gen_cmake_rst.py ..


Generating command line help
----------------------------

The output of

.. code-block:: console

   qibuild --help

or

.. code-block:: console

   qibuild make --help

is automatically generated using:

* The ``help`` argument used in the various `_parsers` functions.

* The first line of the docstring of module corresponding to the action.

So just make sure to write proper docstrings, and to correctly
specify the ``help`` arguments when you configure your parser.


If you think the new action is worth it, you can also patch
the :ref:`qibuild-man-pages`

If you add a new executable, please add the corresponding man page
in ``ref/man``.

This allows the qiBuild debian package to pass ``lintian`` checks.


Documenting configuration files syntax
--------------------------------------

Right now the syntax of the configuration files is not frozen yet.
Just make sure to update the :ref:`qibuild-cfg-syntax` section.

If your changes are incompatible, make sure (and add tests for it!)
that you can convert from the previous version automatically.


.. _qibuild-writing-documentation-python:

Writing Python documentation
-----------------------------

We are using `sphinx autodoc extension <http://sphinx.pocoo.org/ext/autodoc.html>`_ to
generate the :ref:`qibuild-python-doc`, so please make sure to use
valid rst syntax inside your docstrings.

Sphinx's markup is light enough to be used directly in the docstrings, but please
keep the files readable!

As a rule of thumb, if you want to refer to other parts of the documentation, do
it in the ``.rst`` file, and not directly in the ``.py`` file.

This is BAD:

.. code-block:: python

   class Foo:
      """ Does this and that

      .. warning:: A big warning

      Example::

        # A big example

        def tutu:
            foo = Foo()

      .. seealso:

         * :ref:`qibuild-foo-stuff`

      """


.. code-block:: rst

   .. foo.rst

   Foo
   ---

   .. autoclass: Foo


This is OK:

.. code-block:: python

   class Foo:
      """ Does this and that

      .. warning:: A big warning


      """


.. code-block:: rst

   .. foo.rst

   Foo
   ---

   .. autoclass: Foo

      Example::

        # A big example

        def tutu:
            foo = Foo()

      .. seealso:

         * :ref:`qibuild-foo-stuff`


Also, even if the :ref:`modindex` page is generated automatically
py ``Sphinx``, do not forget to update the :ref:`qibuild-python-packages`
``toctree``.
