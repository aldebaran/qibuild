.. _managing-build-configs:

Mananing build configurations
=============================

In this tutorial, you will learn how to use serveral build configurations with
the same sources.

The problem
-----------

Let's say you have a ``foo`` library, with some tests. You want to make the
compilation of the tests optional (because they depend on ``gtest,`` and you do not
want to force your users to have ``gtest``).

A standard CMake way to do it would be:

.. code-block:: cmake

   option(WITH_GTEST "Enable compilation of unit tests" OFF)
   if(WITH_GTEST)
     find_package(GTest Required)
   # ...
     add_test(...)
   else()
   # ...
   endif()

So far so good.

But now you have to pass "-DWITH_GTEST=ON" to all your projects when you
configure them.

Note that ther is a shortcut for that in qibuild CMake API using
:cmake:function:`qi_add_optional_package`:

.. code-block:: cmake

  qi_add_optional_package(GTEST)
  if(GTEST)
  # ....
  else()
  # ...
  endif()

Here, if GTEST is not found, no error is raised, and WITH_GTEST is simply set
to "OFF"...

But let’s assume you really need some flags.

Passing CMake flags with qiBuild
--------------------------------

There are several ways to pass CMake flags to a project managed by qiBuild, in
ascending priority:

* Just once

Simply call:

.. code-block:: console

  $ qibuild configure foo -DWITH_GTEST=ON


* You may want to trigger some flags depending on the toolchain / configuration
  you use.

  For instance, if you want to pass -DWITH_FOO=OFF when you are using the
  toolchain mingw32, you can write something like:

.. code-block:: cmake

    set(WITH_FOO OFF CACHE INTERAL "" FORCE)

in .qi/mingw32.cmake

Using build configurations
---------------------------

qiBuild also lets you to have different settings depending on the toolchain you
use.

The config file will always be found in ``.config/qi/qibuild.xml``

For instance, you could have on a windows machine:

.. code-block:: xml

  <qibuild version="1">
    <defaults>
      <!-- some defaults -->
    </defaults>

    <config name="mingw32">
      <cmake generator="MinGW Makefiles" />
      <env path="c:\MinGW\bin" />
    </config>

    <config name="win32-vs2010">
      <cmake generator="Visual Studio 10" />
    </config>
  </qibuild>
