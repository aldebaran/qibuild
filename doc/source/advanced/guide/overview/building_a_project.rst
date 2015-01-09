.. _qibuild-building-project:

Building a project
==================


Simple build
------------

Let’s assume you only want to compile your project once.

Doing so is easy:

.. code-block:: console

  $ qibuild make foo

Or, to build in release, use:

.. code-block:: console

  $ qibuild make --release foo

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
