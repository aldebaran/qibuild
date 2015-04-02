.. _cmake-install:

Using qi_install functions
==========================

``qi_install`` functions are simply wrappers for ``install`` upstream
CMake functions.

Here are a few concepts you need to understand to properly
use ``qi_install`` functions


Components
----------

The various qi_install_* function deals with the components and respect the
SDK layout for you.


There are 3 sort of dependencies in qibuild, which match 3 install
components:

* ``build``: the dependencies required to build the software. (headers,
  statics libraries, CMake files). You will need that if you want to generate
  a package containing a pre-compiled library for other people to link with, for
  instance.

* ``runtime``: the dependencies required to run the software. (executable,
  dynamic libraries, data, config files)

* ``test`` : the dependencies required to test the software (the gtest library,
  some test executables, ...)


Using ``qibuild install``
--------------------------

By default ``qibuild install <project> <destination>`` install the ``build``
and ``runtime`` components.

If you want to install the ``test`` component too, use ``qibuild install --with-tests``.

If you only want the ``runtime`` component, use ``qibuild install --runtime``.

Note that by default ``CMAKE_INSTALL_PREFIX`` is set to ``/``.

To install directly to ``/usr/local`` do:

.. code-block:: console

    sudo qibuild install --prefix /usr/local /

Install functions, destination, components
-------------------------------------------

Note that the ``qi_create_*`` and the ``qi_stage_lib`` functions create correct install
rules for you by default.

+---------------------------+---------------+-------------------------------------------------------+
|    function               | component     | destination                                           |
+===========================+===============+=======================================================+
|   qi_create_bin           |  runtime      | bin/                                                  |
+---------------------------+---------------+-------------------------------------------------------+
|   qi_create_lib(SHARED)   |  runtime      | lib/ on UNIX, bin/ on windows                         |
+---------------------------+---------------+-------------------------------------------------------+
|   qi_install_conf         |  runtime      | etc/                                                  |
+---------------------------+---------------+-------------------------------------------------------+
|   qi_install_data         |  runtime      | share/                                                |
+---------------------------+---------------+-------------------------------------------------------+
|   qi_create_lib(STATIC)   |  build        | lib/                                                  |
+---------------------------+---------------+-------------------------------------------------------+
|   qi_stage_lib(foo)       |  build        |  share/cmake/modules/foo/foo-config.cmake             |
+---------------------------+---------------+-------------------------------------------------------+
|   qi_install_header       |  build        |  include/                                             |
+---------------------------+---------------+-------------------------------------------------------+
|   qi_create_test_helper   |  test         | bin/                                                  |
+---------------------------+---------------+-------------------------------------------------------+

Other use cases
---------------

If you don't want the executable to be installed
(because it's just used at build time, for instance), you can use:

.. code-block:: cmake

  qi_create_bin(foo NO_INSTALL)

If you want to install an executable that is NOT the result of a compilation
(for instance a script), you can use :cmake:function:`qi_install_program`

If you want to install something in your development install that does not fit
in these destinations (say, an example), you can use the generic
:cmake:function:`qi_install` function with ``DESTINATION`` and ``COMPONENT``
arguments.


Special features
-----------------

:cmake:function:`qi_install` ends up calling regular install() CMake functions, but there
are some differences, here are a few

Check of arguments
++++++++++++++++++

If you try to install a file that does not exist,
using `install()` will exit during installation, but qi_install will
exit during configuration.
This does no prevent you from installing generated files, but you have to make
sure the are generated *before* creating the install rule.

.. code-block:: cmake

   # Always generate files in cmake build dir:
   set(_out ${CMAKE_CURRENT_BINARY_DIR}/foobar)
   configure_file(foobar.in "${_out}")
   qi_install("${_out}"
     DESTINATION /etc/init.d/
     )

   # Note the trailing "/" at the end of the DESTINATION argument.

   # Do NOT use:
   qi_install("${_out}"
     DESTINATION /etc/init.d/foobar
     )

   # or you'll end up with /etc/init.d/foobar/foobar ...

Support of glob and directories
+++++++++++++++++++++++++++++++

Please not that on top of this, you can use directories, globbing expressions
and list of files as arguments on all qi_install_* functions.

For instance

.. code-block:: cmake

  qi_install(foo/bar/ *.txt spam.cfg eggs.cfg DESTINATION "prefix")

will install:

* directory foo/bar to "prefix/bar"
* every .txt file in current directory to "prefix"
* the spam and eggs cfg file to "prefix"

Note the glob is not recursive by default.

If you really need it, just use:

.. code-block:: cmake

   qi_install(foo/*.hpp RECURSE)



"IF" keyword
++++++++++++

Instead of using

.. code-block:: cmake

  if(FOO)
    qi_install(.... )
  endif()

you can use

.. code-block:: cmake

   qi_install(.... IF FOO)


SUBFOLDER and KEEP_RELATIVE_PATHS keywords
++++++++++++++++++++++++++++++++++++++++++

``qi_install`` functions accept either a ``SUBFOLDER`` or a
``KEEP_RELATIVE_PATHS`` keyword.

It is easier to understand the meaning of these keywords by an example.


Using SUBFOLDER
~~~~~~~~~~~~~~~

You should use this for instance with headers in several different folders (a
bit like an autotools project)::

    sources:                      destination
      foo                          include
      |__ include                  |__ foo
          |__ foo.h                       |__ foo.h
          |__ bar.h                       |__ bar.h
      config.h (generated)                |__ config.h


.. code-block:: cmake

    qi_install_header(foo/include/foo.h
                      foo/include/bar.h
                      ${CMAKE_BUILD_DIR}/config.h
                      SUBFOLDER foo)

:cmake:function:`qi_install_header` will set DESTINATION "include" for you,
but you need 'SUBFOLDER foo' argument to tell CMake to install files
to include/foo, regardless their original path.



Using KEEP_RELATIVE_PATHS
~~~~~~~~~~~~~~~~~~~~~~~~~

You should you this for instance  with headers following the exact same
hierarchy in the source tree and when installed (a bit like boost)::

    sources                         destination
      libfoo                        include
      |__ foo                       |__ foo
          |__ foo.h                     |__ foo.h
          bar                           bar
          |__ bar.h                     |__ bar.h
              baz                           baz
              |__ baz.h                     |__ baz.h


.. code-block:: cmake

    qi_install_header(foo/foo.h
                      bar/bar.h
                      bar/baz/baz.h
                      KEEP_RELATIVE_PATHS)

:cmake:function:`qi_install_header` will set DESTINATION "include" for you, and you do not
need ``SUBFOLDER`` because ``KEEP_RELATIVE_PATHS`` is set.
