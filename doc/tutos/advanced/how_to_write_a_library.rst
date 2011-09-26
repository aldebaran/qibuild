.. _how-to-write-a-library:

How to write a library
======================

This is merely a convention, but you are advised to follow it, especially if
you are working in a large project.

Let's say you have a foo library.

You have the following files:

* foo.h : the public header of the foo library. It contains the public API, and
  include the least possible number of other headers. (Use of forward
  declarations, and PIMPL implementations are recommanded)

* foo.cpp : implementation of the foo.h functions

* foo_private.h : private header of the foo library. This one may include
  third-party headers (say zeromq.h), without having the foo.h header depending
  on zeromq.h, which is nice for the users of your library. If you link
  statically with zeromq, users of foo won't even need to know about zeromq
  (well, this is true if foo is a dynamic library, but that's an other topic)

* foo_private.cpp : private implementation.

* foo_test.cpp : You would not dare writing a library without unit tests, would
  you?

Proposed layout
---------------

This is what your layout should look like::

  fooproject
  |__ libfoo
      | CMakeLists.txt
      |__ foo
      |   |__ foo.h
      |__ src
      |   |__ foo.cpp
      |   |__ foo_private.h
      |   |__ foo_private.cpp
      |__ test
          |__ CMakeLists.txt
          |__ foo_test.cpp

* The full path to the public header is foo/foo/foo.h. Note that the name of the
  root directory is libfoo

* The private code is put in a src sub-directory. Private and public directories
  are separated, it's easy to search only in public headers.

CMake
-----

Here's what the CMakeLists should look like

.. code-block:: cmake

  # Main CMakeLists
  cmake_minimum_required(VERSION 2.8)
  include("qibuild.cmake")
  project(fooproject)

  add_subdirectory(foo)
  add_subdirectory(foo/test)


  include_directories(".")

  # optional if you have private headers
  include_directories("src")


  qi_create_lib(foo
    SRC foo/foo.h
        foo/foo.cpp
        src/foo_private.h
        src/foo_private.cpp
  )

  qi_install_header(KEEP_RELATIVE_PATHS foo/foo.h)

  qi_stage_lib(foo)

  # foo/test/CMakeLists.txt
  qi_create_gtest(foo_test
    SRC
      foo_test.cpp
    DEPENDS
      gtest
      foo)

Please note that the location of the cmake list file matters.

Rationale
---------

You will note that:

* The only time we call include_directories() is when we are staging the foo
  library.

* The foo.h header is in a directory named foo, and qi_install_header() uses
  this directory as first argument. It's advised you use the same name for the
  target and the subdirectory.

* Everything that need a foo header must use

.. code-block:: cpp

  #include <foo/...>

This way, we are sure that the code we use can be re-distributed when the
headers are installed, and that the path to find the headers while in the
source tree does not differ from the paths to find the installed headers. This
works because:

  * We have put foo.h in a foo subdirectory.

  * We have used :ref:`qi_install_header` with the correct SUBFOLDER
    argument

* The test can use both the public API and the private implementation

* Let's assume you have two libraries, foo and bar, and a foobar executable
  that needs code from foo and bar.

With the proposed layout, you have something like::

  libfoo
  |__ foo
  |    |__ foo
  |    |    |__ foo.h
  |    bar
  |    |__ bar
  |        |__ bar.h
  foobar
      |__ foobar.cpp

You may want to get rid of the useless redundancy foo/foo, bar/bar, and do this
instead::

  lib
  |__ foo
  |    |__ foo.h
  |    bar
  |    |__ bar.h
  foobar
      |__ foobar.cpp

But, let's assume you have

.. code-block:: cmake

  qi_use_lib(foobar foo)

instead of

.. code-block:: cmake

  qi_use_lib(foobar foo bar)

In the first layout, you will have an error during compile time, looking like::

  bar/bar.h : no such file or directory

(because the include directory that has been staged for foo is different from
the include directory that has been staged for bar) But, using the second
layout, you will have an error during link time, looking like::

  undefined reference to `bar_func'

(because the include directory that was staged was always the same: lib)

.. note:: For large libraries, also consider using submodles. The
   documentation can be found :ref:`here <using-submodules>`

.. FIXME
  The complete sources of the project can be found here
  Warning, you will need GTest to compile the project
