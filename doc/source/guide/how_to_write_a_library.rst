.. _how-to-write-a-library:

How to write a library
======================

This is merely a convention, but you are advised to follow it, especially if
you are working in a large project.

Let's say you have a ``foo`` library.

You have the following files:

* ``foo.hpp``: the public header of the ``foo`` library. It contains the public
  API, and include the least possible number of other headers. (Use of forward
  declarations, and PIMPL implementations are recommanded)

* ``foo.cpp`` : implementation of the ``foo.hpp`` functions

* ``foo_private.hpp``: private header of the ``foo`` library. This one may
  include third-party headers (say ``zeromq.h),`` without having the
  ``foo.hpp`` header depending on ``zeromq.h,`` which is nice for the users of
  your library. If you link statically with ``zeromq,`` users of ``foo`` won't
  even need to know about ``zeromq``
  (well, this is true if ``foo`` is a dynamic library, but that's an other
  topic)

* ``foo_private.cpp`` : private implementation.

* ``test_foo.cpp`` : You would not dare writing a library without unit tests,
  would you?

Proposed layout
---------------

This is what your layout should look like::

  fooproject
  |__ libfoo
      | CMakeLists.txt
      |__ foo
      |   |__ foo.hpp
      |__ src
      |   |__ foo.cpp
      |   |__ foo_private.hpp
      |   |__ foo_private.cpp
      |__ test
          |__ CMakeLists.txt
          |__ foo_test.cpp

* The full path to the public header is ``foo/foo/foo.hpp``. Note that the name
  of the root directory is ``libfoo``

* The private code is put in a ``src`` sub-directory. Private and public
  directories are separated, it's easy to search only in public headers.

Note: you can download an archive containing the foo project here:
:download:`fooproject.zip </samples/fooproject.zip>`

CMake
-----

Here's what the ``CMakeLists.txt`` should look like


.. literalinclude:: /samples/fooproject/libfoo/CMakeLists.txt
   :language: cmake

Please note that the location of the CMake list file matters.

Rationale
---------

You will note that:

* The only time we call ``include_directories()`` is when we are staging the foo
  library.

* The ``foo.hpp`` header is in a directory named ``foo``, and will be
  installed to ``foo/foo.hpp``.
  It's advised you use the same name for the target and the subdirectory.

* Everything that need a ``foo`` header must use

.. code-block:: cpp

  #include <foo/...>

This way, we are sure that the code we use can be re-distributed when the
headers are installed, and that the path to find the headers while in the
source tree does not differ from the paths to find the installed headers. This
works because:

* We have put ``foo.hpp`` in a ``foo`` subdirectory.

* We have used :cmake:function:`qi_install_header` with the ``KEEP_RELATIVE_PATHS``
  argument. You could also have used it with a ``SUBFOLDER`` argument, like
  this:

.. code-block:: cmake

   qi_install_header(foo/foo.hpp SUBFOLDER foo)

* Let's assume you have two libraries, ``foo`` and ``bar``, and a ``foobar``
  executable that needs code from ``foo`` and ``bar``.

With the proposed layout, you have something like::

  foooproject
  |__ libfoo
  |    |__ foo
  |    |    |__ foo.hpp
  |    libbar
  |    |__ bar
  |        |__ bar.hpp
  |__ foobar
      |__ foobar.cpp

You may want to get rid of the useless redundancy foo/foo, bar/bar, and do this
instead::

  fooproject
  |__ foo
  |   |__ foo.hpp
  |   bar
  |   |__ bar.hpp
  foobar
      |__ foobar.cpp

But, let's assume you have

.. code-block:: cmake

  qi_use_lib(foobar foo)

instead of

.. code-block:: cmake

  qi_use_lib(foobar foo bar)

In the first layout, you will have an error during compile time, looking like::

  bar/bar.hpp : no such file or directory

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
