.. _writing-a-config-cmake:

Writing a custom -config.cmake module file
==========================================


Let use assume you want to use the ``foo`` library, and no
``FindFoo.cmake`` for ``foo-config.cmake`` exist.

(Because it is not known enough to be in standard CMake
modules, or because the ``foo`` project does not use CMake
as a build system, or for whatever reason)

In anycase, if you do have access to a ``foo-config.cmake`` of
a ``FindFoo.cmake``, please just use it!

Note that ``qi_use_lib(foo)`` does not need a specific
``foo-config.cmake`` to work.

It is only necessary that the ``foo-config.cmake`` code exports
``FOO_INCLUDE_DIRS`` and ``FOO_LIBRARIES``.



Simplest case
-------------

Here we assume that the ``foo`` library only needs an include directory,
and the name of the library is the same in debug and in release.

The canonical ``foo-config.cmake`` should look like

.. code-block:: cmake

   clean(FOO)
   fpath(FOO foo/foo.h)
   flib(FOO foo)
   export_lib(FOO)


Here we assume that the library is named ``foo.lib`` for
Visual Studio, ``libfoo.a`` or ``libfoo.so`` for Linux, or
``libfoo.a`` or ``libfoo.dylib`` for Mac.

We also assume that the library is in a `/lib` directory
and the header in a `include` directory, and from a prefix
where CMake can find it, either because:

* foo is in a package in a toolchain following the sdk layout

* foo is installed on the system, so the prefix is ``/usr/``
  or ``/usr/local``.


This should cover 90% of the use cases.

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



Finding libraries with different names
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

Headers-only libraries
----------------------

Some libraries are only made of headers! Let's assume this is the case for
foo.

What you have to do here is:

.. code-block:: cmake

  fpath(FOO foo/foo.h)
  export_header(FOO)

In a nutshell:

* No ``flib`` needed.

* ``export_header`` instead of ``export_lib``

Finding in non standards paths
------------------------------

Sometimes want you want to find is not under a standard location,
such as ``/usr/local/include`` or ``/usr/include``.

So, for instance let's assume the foo library is in ``/opt/bar/lib/libfoo.so``
and the header in ``/opt/bar/include/foo/foo.h``

All you have to do is to specify PATHS as you would do if you used the normal
``find_path`` CMake method.

So in our case

.. code-block:: cmake


   fpath(FOO foo/foo.h PATHS /opt/bar/include)
   flib(FOO NAMES foo PATHS /opt/bar/lib)

Finding pkg-config libraries
----------------------------


If the ``foo`` library comes with a ``foo-1.0.pc`` file, you
should use the ``PkgConfig`` module from CMake, like this

.. code-block:: cmake

  clean(FOO)
  find_package(PkgConfig)
  pkg_check_modules(FOO foo-1.0)
  export_lib_pkgconfig(FOO)

