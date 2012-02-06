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

They also help you producing 'runtime' packages (containing just what is necessary
to run your software), or 'development' packages (containing everything in the
runtime package, plus all that is necessary to use your : headers, library,
cmake config files, et al.)

Runtime versus development installation
---------------------------------------

Here are the components that will be used during a runtime install

+---------------+---------------------------+------------------------------------+
| component     |    function               | destination                        |
+===============+===========================+====================================+
| "binary"      |   qi_create_bin           | bin/                               |
+---------------+---------------------------+------------------------------------+
| "lib"         |   qi_create_lib(SHARED)   | lib/ on UNIX, bin/ on windows      |
+---------------+---------------------------+------------------------------------+
| "conf"        |   qi_install_conf         | etc/                               |
+---------------+---------------------------+------------------------------------+
| "data"        |   qi_install_data         | share/                             |
+---------------+---------------------------+------------------------------------+
| "doc"         |   qi_install_doc          | share/doc                          |
+---------------+---------------------------+------------------------------------+

Note that :cmake:function:`qi_create_bin` and :cmake:function:`qi_create_lib` create the install
rules for you by default.
If you don't what the executable to be installed (because it's just a test, for instance, you can use:

.. code-block:: cmake

  qi_create_bin(foo NO_INSTALL)

If you want to install an executable that is NOT the result of a compilation
(for instance a script), you can use :cmake:function:`qi_install_program`


When doing a normal install, you will get the previous component, plus
the following ones

+---------------+---------------------------+------------------------------------+
| component     |   function                |  destination                       |
+===============+===========================+====================================+
| "static-lib", |   qi_create_lib(STATIC)   |  lib/                              |
+---------------+---------------------------+------------------------------------+
| "cmake"       |   qi_stage_lib            |  share/cmake/modules/              |
+---------------+---------------------------+------------------------------------+
| "header"      |   qi_install_header       |  include/                          |
+---------------+---------------------------+------------------------------------+

If you want to install something in your development install that does not fit
in these components (say, an example), you can use the generic
:cmake:function:`qi_install` function

For instance

.. code-block:: cmake

  qi_install(foo_example bar_examples DESTINATION examples KEEP_RELATIVE_PATHS)

will give you::

  sources                       destination
                                 examples
  foo_example                    |__ foo_example
  |__ CMakeLists                    |__ CMakeLists
  |__ foo.cpp                       |__ foo.cpp
  bar_example                       bar_example
  |__ CMakeLists                    |__ CMakeLists
  |__ bar.cpp                       |__ bar.cpp

Also, to install a ``README`` at the root of your package you could do:

.. code-block:: cmake

  qi_install(doc/README DESTINATION ".")

Since no component as been given, this files won't be in the runtime install.


Special features
-----------------

:cmake:function:`qi_install` ends up calling regular install() CMake functions, but there
are some differences, here are a few

Check of arguments
++++++++++++++++++

If you try to install a file that does not exists,
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

  qi_install(foo/bar/ \*.txt spam.cfg eggs.cfg DESTINATION "prefix")

will install:

* directory foo/bar to "prefix/bar"
* every .txt file in current directory to "prefix"
* the spam and eggs cfg file to "prefix"

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

    qi_install_header(foo
                     HEADERS
                       foo/include/foo.h
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

    qi_install_header(foo
                      HEADERS
                        foo/foo.h
                        bar/bar.h
                        bar/baz/baz.h
                      KEEP_RELATIVE_PATHS)

:cmake:function:`qi_install_header` will set DESTINATION "include" for you, and you do not
need ``SUBFOLDER`` because ``KEEP_RELATIVE_PATHS`` is set.

