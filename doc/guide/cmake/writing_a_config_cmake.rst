.. _writing-a-config-cmake:

Writing a custom -config.cmake module file
==========================================


Let use assume you want to use the ``foo`` library, and no
``FindFoo.cmake`` for ``foo-config.cmake`` exist.

(Because it is not known enough to be in standard CMake
modules, or because the ``foo`` project does not use CMake
as a build system, or for whatever reason)

In anycase, if you do have access, please just use it!

Note that ``qi_use_lib(foo)`` does not need a specific
``foo-config.cmake`` to work.

It is only necessary that the ``foo-config.cmake`` code exports
``FOO_INCLUDE_DIRS`` and ``FOO_LIBRARIES``.



Simplest case
-------------

Here we assume that the ``foo`` library only needs an include directory,
and tht the name of the library is the same in debug and in release.

The canonical ``foo-config.cmake`` should look like

.. code-block:: cmake

   clean(FOO)
   fpath(FOO foo/foo.h)
   flib(FOO foo)
   export_lib(FOO)


Here we assume that the library is named ``foo.lib`` for
Visual Studio, ``libfoo.a`` or ``libfoo.so`` for Linux, or
``libfoo.a`` or ``libfoo.dylib`` for Mac.


If the ``foo`` library is open source, do not hesitate to submit
a patch to integrate ``foo-config.cmake`` with other qibuild cmake modules.

If not, you can simply add ``foo-config.cmake`` inside
your project, for instance in
``src/bar/cmake/modules/foo-config.cmake``, and
modify ``src/bar/CMakeLists.txt`` too look like:

.. code-block:: cmake

   cmake_minimum_required(VERSION 2.8)
   project(bar)
   include("qibuild.cmake")

   list(APPEND CMAKE_FIND_ROOT_PATH
    ${CMAKE_SOURCE_DIR}/cmake/modules)

   qi_create_bin(bar bar.cpp)
   qi_use_lib(bar foo)



Finding libraires with different names
--------------------------------------


You could have to handle the case where the library is named
``libfoo-1.2`` on linux

In this case, simply add some calls to ``flib``

.. code-block:: cmake

  flib(FOO foo)
  if (UNIX)
    flib(FOO foo-1.12)
  endif()


If the ``foo`` library depends on other libraries, for instance
``foo-base``, ``foo-client`` , ``foo-server``, you can use

.. code-block:: cmake

   flib(FOO foo foo-base foo-client foo-server)


Note: here we assume that ``libfoo.so``, ``libfoo-base.so``,
``libfoo-client.so`` and ``libfoo-server.so`` are part of the
same package.

If ``foo`` depends on an library from an other package (say ``spam``),
you should write a ``spam-config.cmake`` and use something like

.. code-block:: cmake

   clean(FOO)
   # caliing flib, fpath as usual
   qi_set_global(FOO_DEPENDS spam)
   export_lib(FOO)


Finding include directories with prefixes
-----------------------------------------


Assuming ``foo.h`` is in ``/usr/local/include/foo/foo.h``, you can
use either:

.. code-block:: cmake

   fpath(FOO foo/foo.h)

In this case, ``FOO_INCLUDE_DIRS`` will equal ``/usr/local/include``,
so you will have to use

.. code-block:: cpp

   #include <foo/foo.h>

Or you can use::

  fpath(FOO foo.h PATH_SUFFIXES foo)

In this case, ``FOO_INCLUDE_DIRS`` will equal
``usr/local/include/foo``, so you will have to use

.. code-block:: cpp

   #include <foo.h>


Finding pkg-config libraries
----------------------------


If the ``foo`` library comes with a ``foo-1.0.pc`` file, you
should use the ``PkgConfig`` module from CMake, like this

.. code-block:: cmake

  clean(FOO)
  find_package(PkgConfig)
  pkg_check_modules(FOO foo-1.0)
  export_lib_pkgconfig(FOO)

