.. _qibuild-managing-deps:

Managing dependencies between projects
======================================

In this tutorial, you will learn how to manage dependencies between projects.

Requirements
------------

We will assume you have a properly configured qiBuild
worktree, and that you have managed to compile a basic project.

Please make sure you have follow the
:ref:`getting started tutorial <qibuild-getting-started>`.

Overview
--------

We are going to create two separate projects: ``hello`` and ``world,`` where
``hello`` depends on the compiled library found in ``world.``

The ``world`` project contains sources to build a dynamic library
(``libworld.so`` or ``world.dll``)

The ``hello`` project contains source to build an executable named ``hello``
which depends on the ``world`` library.

It also contains a small test that simply tries to launch ``hello.``

The sources of this example can be found here:
:download:`helloworld.zip </samples/helloworld.zip>`

Extract the archive in your qiBuild worktree, you should end up with something
looking like::

  .qi
  |__ qibuild.xml
  world
  |__ qiproject.xml
  |__ CMakeLists.txt
  |__ world
      |__ world.hpp
      |__ world.cpp
  hello
  |__ qiproject.xml
  |__ CMakeLists.txt
  |__ main.cpp



qiBuild in action
------------------

Configuring and building the hello project is as easy as

.. code-block:: console

  $ qibuild configure hello
  $ qibuild make hello
  $ qibuild test hello


For this to work, you only have to write two ``qiproject.xml`` files

The first one in ``QI_WORK_TREE/world/qiproject.xml`` simply tells
qibuild that there is a project named ``world`` in
``QI_WORK_TREE/world``

.. code-block:: xml

   <project name="world" />

The second one in ``QI_WORK_TREE/hello`` tells ``qibuild``
there is a project named ``hello`` in ``QI_WORK_TREE/hello``,
and that it depends on the ``world`` project:

.. code-block:: xml

  <project name="hello">
    <depends buildtime="true" runtime="true"
      name="world"
    />
  </project>

You can see that configuring ``hello`` caused the ``world`` project to be
configured too, and that building ``hello`` also built the ``world`` project.

On Windows, the ``world`` DLL was copied right next to ``hello.exe,`` so
running ``qibuild test hello`` just worked.

If you are using Visual Studio, you can open ``hello.sln`` in
``QI_WORK_TREE/hello/build-.../hello.sln``, select "hello" as startup project,
and start debugging hello_d.exe right away.

.. warning:: If you try to compile hello in release, you’ll get an
  error because "world" has not been compiled in release, so world.lib could
  not found.

  Simply run

  .. code-block:: console

    $ qibuild configure --release world
    $ qibuild make --release world

  And try again.
