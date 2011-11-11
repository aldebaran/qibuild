.. _qibuild-documentation:

QiBuild documentation
=====================


Introduction
------------

QiBuild aims to make compilation of your sources easy. It manages dependencies
between projects and supports cross-compilation.

By default QiBuild uses libraries provided by your system, but you can also use
qiToolchain to manage sets of pre-compiled packages (called toolchains) if you
want. Cross-compilation is then just a matter of using a specific toolchain.

QiBuild is truly cross-platform: it is tested on Linux, Mac and Windows. Being
based on the well-known CMake build system, it allows you to use your existing
tools such as gcc, Makefile, or Visual Studio.

The QiBuild framework tries hard to stand out of your way: it remains close to
standards, and will play nice with other build systems.

QiBuild is composed of two parts:

* the QiBuild CMake framework, that simplifies authoring CMakeLists.txt.

* the qibuild/qitoolchain command line tools, that helps build projects while
  taking dependencies into account and generate re-destributable binary
  packages


QiBuild in 5 minutes
--------------------

* Create a worktree:

.. code-block:: console

   $ cd ~/src
   $ qibuild init


* Create a ``world`` library in the ``world``
  project, in ``src/world``

.. code-block:: console

   $ cd ~/src/world
   $ $EDITOR CMakeLists.txt

.. code-block:: cmake

    cmake_minimum_required(VERSION 2.8)
    project(world)
    include("qibuild.cmake")

    qi_create_lib(world world/world.hpp world/world.cpp)
    qi_stage_lib(world)


* Create a ``hello`` in the ``hello`` project, in
  ``src/hello``, using the ``world`` library:

.. code-block:: console

   $ cd ~/src/hello
   $ $EDITOR qibuild.manifest


.. code-block:: ini

   [project hello]
   depends = world

.. code-block:: console

   $ $EDITOR CMakeLists.txt


.. code-block:: cmake

    cmake_minimum_required(VERSION 2.8)
    project(hello)
    include("qibuild.cmake")

    qi_create_bin(hello main.cpp)

.. code-block:: console

   $ cd ~/src
   $ qibuild configure hello

   Call cmake on world, then hello

   $ qibuild make hello

   Build world, then hello, automagically
   linking `src/hello/build/sdk/bin/hello` with
   `src/world/build/sdk/lib/libworld.so`


* Distribute the world project to the world

.. code-block:: console

   $ qibuild package world

   Generate world package in ~/src/packages/world.tar.gz


.. code-block:: xml

   <toolchain>
     <package
      name="world"
      url="htpp://example.com/world.tar.gz"
     />
    </toolchain>

On a other machine:

.. code-block:: console

   $ qitoolchain init $NAME htpp://example.com/feed.xml

   Add package from htpp://example.com/world.tar.gz to
   a toolchain named $NAME

   $ qisrc add git@git.example.com/hello.git

   Get hello sources from a git repository

   $ qibuild configure -c $NAME hello

   No need for world sources, using pre-compiled library
   from the world package


References
----------

.. toctree::
   :maxdepth: 2

   cmake/index

   man/index



Tutorials
---------

Learn how to use the QiBuild framework to build your C++ projects.


.. toctree::
   :maxdepth: 2

   tutos/beginner
   tutos/intermediate
   tutos/advanced


Hacking
-------

Read this if you want to contribute to QiBuild

.. toctree::
   :maxdepth: 1

   hacking/cmake/coding_guide
   hacking/python/coding_guide
   hacking/cmake/qibuild/rosbuild
   hacking/cmake/qibuild/under_the_hood
