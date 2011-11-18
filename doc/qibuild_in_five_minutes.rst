.. _qibuild-in-five-minutes:

qiBuild in five minutes
=======================


Create a worktree:

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

* Make world depend on ``ode``

.. code-block:: console

    $ $EDITOR qibuid/modules/ode-config.cmake

.. code-block:: cmake

   clean(ODE)
   fpath(ODE ode/ode.h)
   flib(ODE ode)
   export_lib(ODE)

.. code-block:: cmake

   qi_use_lib(world ODE)


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


* Distribute the world project to the world, step 1:
  Add install rules for world header

.. code-block:: cmake

   qi_install_header(world/world.hpp SUBFOLDER world)

* Distribute the world project to the world, step 2:
  Generate world package in ~/src/packages/world.tar.gz
  using cmake install rules.

.. code-block:: console

   $ qibuild package world


* Distribute the world project to the world, step 3:
  Upload the package along with a feed description:

.. code-block:: xml

   <toolchain>
     <package
      name="world"
      url="htpp://example.com/world.tar.gz"
     />
    </toolchain>

* Use the world package from an other machine:

.. code-block:: console

   $ qitoolchain init $NAME htpp://example.com/feed.xml

   Add package from htpp://example.com/world.tar.gz to
   a toolchain named $NAME

   $ qisrc add git@git.example.com/hello.git

   Get hello sources from a git repository

   $ qibuild configure -c $NAME hello

   No need for world sources, using pre-compiled library
   from the world package


