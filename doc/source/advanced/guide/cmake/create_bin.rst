.. _cmake-create-bin:

Creating a binary
=================

In this tutorial, we will learn how to create executables with the qiBuild
framework

Requirements
------------

We assume you have followed the :ref:`qibuild-getting-started` tutorial.

Basic CMake
-----------

Every CMake project should begin with something like:

.. code-block:: cmake

  cmake_minimum_required(VERSION 2.8)
  find_packagte(qibuild)
  project(foo)

The first line is required by the CMake standards.

The second line let you use the ``qibuild`` cmake framwork.

The project() call is good practice, and is used by several IDEs.

Adding an executable
--------------------


To add an executable, simply call :cmake:function:`qi_create_bin`. The first argument is the name
of the executable, followed by the sources of the executable.

The paths of the sources are relative to the path where the CMakeLists is
found, so you should create the main.cpp right next to the CMakeLists

.. code-block:: cmake

  qi_create_bin(foo main.cpp)

If you are on UNIX, the executable will end up in ``build/sdk/bin/foo``
If you are using Visual Studio, the executable will be in:

* ``build/sdk/bin/foo_d.exe`` (if you chose to build in debug)

or in

* ``build/sdk/bin/foo.exe`` (if you chose to build in release)

.. note:: To run directly the foo executable from Visual Studio, simply
   right-click on the foo project and select ``Choose as start up project``, then
   press F5 as usual.
   If you try to run the ``ALL`` project which is selected by default, you will
   get an error message because the ``ALL`` project does not correspond to any
   executable.

