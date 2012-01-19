
.. toctree::
    :hidden:

    managing_deps
    searching
    shared_libs


.. _qibuild-cmake-design:

qiBuild CMake framework design
==============================

General design decisions
------------------------


qiBuild CMake framework is designed around a few principles:

* Staying close to the standards

* Trying to follow CMake best practices (from CMake wiki
  or in /usr/share/cmake-2.8/Modules/readme.txt)

* Do not get into the developer's way

* Play nice with other build frameworks:

  * Every custom CMake function is prefixed with ``qi_``
  * Every custom CMake files is in a ``qibuild`` subidrectory
  * Generated CMake code is always pure, standard CMake code
  * Absolutely NO environment variable is required, except for
    ``PATH`` and ``PYTHONPATH``


.. _qibuild-cmake-concepts:

qiBuild CMake Concepts
----------------------

.. glossary::

  **SDK**
    A directory containing files used to compile other code.
    A SDK always has a **layout**, following POSIX and cmake
    conventions.

Here is an example of a SDK containing the ``bar`` executable,
a ``bar.cfg`` configuration file for ``bar,`` a ``foo`` library
with the ``foo-config.cmake`` file, and the ``foo.h`` hader::


    <sdk>
    |__ include
        |__ foo
             |__ foo.h
    |__ lib
        |__  libfoo.a
        |__  libfoo.a
        |__  foo.lib
    |__ bin
        |__ bar
        |__ foo.dll
        |__ bar.exe
    |__ cmake
        |__ foo
            |__ foo-config.cmake
    |__ etc
           |__ bar
               |__ bar.cfg


  The root of a SDK can safely be added to ``CMAKE_FIND_ROOT_PATH``
  variable.

.. glossary::

  **package**
    A package is simply an archive containing the one or several SDKs.
    If always has a ``.tar.gz`` extension on UNIX, and a ``.zip`` extension
    on windows.

    All files are in the same top dir, so it is safe to extract it everywhere.

    Some packages may also need a toolchain file.

.. glossary::

  **toolchain file**
    Usually, your are supposed to use a toolchain file when cross-compiling
    with CMake, with the ``CMAKE_TOOLCHAIN_FILE`` variable.

For qiBuild, we extend the usage of the toolchain file a little bit.

In a toolchain file, you may:

* Force a compiler (which is the main purpose of a toolchain file)

* Set some CMake flags (for instance CMAKE_OSX_ARCHITECTURES)

* Or set some CMake variables like CMAKE_FIND_ROOT_PATH


A package can be associated to a toolchain file.

For instance, you may have a simple package ``foobar`` containing the result
of the installation of the ``bar`` executable and the ``foo libaray``,
requiring now toolchain file at all, or a complex package name ``geode-ctc``
containg some libs in  ``ctc/sysroot/usr/lib``, and a cross-compiler in
``ctc/cross``, and a toolchain file forcing the compiler to be
``ctc/cross/bin/gcc``, and setting CMAKE_FIND_ROOT_PATH to ``ctc/sysroot``.

.. glossary::

  **toolchain**
    A toolchain is simply a collection of :term:`packages <package>`

  **feed**
    A feed is a smiple XML file describing a toolchain: its location,
    and the packages that are in it.


Overviews
---------

You can read the following sections if you want to understand deeply
how qibuild works, under the hood.

* :ref:`qibuild-managing-deps-overview`
* :ref:`qibuild-search-order`
* :ref:`qibuild-shared-libs`


