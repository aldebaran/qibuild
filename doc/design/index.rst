.. toctree::
   :hidden:

   cmake/index
   python/index

.. _qibuild-design:

qiBuild design
==============


qiBuild source code is divide into two loosely-coupled components.


qiBuild CMake framework
-----------------------


The CMake framework is composed of two parts:

* A bunch of files containing nice wrappers for CMake functions,
  aim to simplify authoring of CMakeLists files, which
  constitutes the :ref:`qibuild-cmake-api`

* A set of `-config.cmake` files, written because upstream
  CMake modules files are missing or not correct.
  You can learn about about this config files by following
  the :ref:`writing-a-config-cmake` tutorial.


But of course, the main feature of the qiBuild CMake
framework is to allow you to easily manage dependencies
between project.

For a more detailed description of how this works,
please read the :ref:`qibuild-cmake-design` section.



qiBuild command line tools
--------------------------

First note that the qibuild command line tools are absolutely
not necessary use the qiBuild CMake framework.

The qibuild tools are all written in Python.

The :ref:`porting-to-qibuild` guide never uses the qibuild command
line, for instance.

The coupling between the Python command line tools and the CMake
framework is very loose.

qibuild command line only generates small bits of CMake code:

* A `dependencies.cmake` in the build directory, which is
  only useful if your project depends on library not found on
  your system, or if the qibuild CMake framework is not
  installed on your system.
  (And this file is simply NOT included if it does not exist)

* A CMake toolchain file when using toolchains. (more on this later)


For a more detailed description of the qibuild features
and how the are implemented, please read the :ref:`qibuild-python-design` section.


