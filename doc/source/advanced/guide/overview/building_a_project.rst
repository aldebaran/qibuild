.. _qibuild-building-project:

Building a project
==================


Simple build
------------

Let's assume you only want to compile your project once.

Doing so is easy:

.. code-block:: console

  $ qibuild make foo

By default the binaries are built in debug.

To build in release, you must first re-run ``qibuild configure``
with a ``--release`` argument, then call ``qibuild make``

.. code-block:: console

  $ qibuild configure foo --release
  $ qibuild make foo

Behind the scenes, ``qibuild configure --release`` just sets
``CMAKE_BUILD_TYPE`` to ``Release``. You can specify arbitrary
build types with ``qibuild configure --build-type``, for instance:

.. code-block:: console

  $ qibuild configure --build-type=RelWithDebInfo

Using an IDE
------------

qiBuild is based on CMake, which in turns knows how to generate project files
for many of IDEs : Xcode, Eclipse, Visual Studio.
Here we are only dealing with the details for:

* QtCreator on Mac and Linux

* Visual Studio on Windows.

See:

* :ref:`qibuild-visual-studio`
* :ref:`qibuild-qtcreator`

qiBuild is known to work fine with these IDEs, there may be some work to do to
be able to use Xcode or Eclipse. Patches and tutorials welcome !


Using Aldebaran packages
-------------------------

See: :ref:`qibuild-using-aldebaran-packages`
