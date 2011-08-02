Managing dependencies between projects
======================================


In this tutorial, you will learn how to manage dependencies between projects.

Requirements
------------

In this tutorial, we will assume you have a properly configured QiBuild
worktree, and that you’ve managed to compile a basic project.

Overview
--------

We are going to create two separate projects: hello and world, where hello
depends on the compiled library found in world.

The world project contains sources to build a dynamic library (libworld.so or
world.dll)

The hello project contains source to build an executable named hello which
depends on the world library.

It also contains a small test that simply tries to launch hello.

The sources of this example can be found here

Extract the archive in your QiBuild worktree, you should end up with something
looking like::

  .qi
  |__ build.cfg
  world
  |__ CMakeLists.txt
  |__ qibuild.cmake
  |__ qibuild.manifest
  |__ world
      |__ world.h
      |__ world.cpp
  hello
  |__ CMakeLists.txt
  |__ qibuild.cmake
  |__ qibuild.manifest
  |__ main.cpp

QiBuild in action
------------------

Configuring and building the hello project is as easy as::

  qibuild configure hello
  qibuild make hello
  qibuild test hello

You can see that configuring hello caused the world project to be configured
too, and that building hello also built the world project.

On windows, the world DLL was copied right next to hello.exe, so running
qibuild test hello just worked.

If you are using visual studio, you can open hello.sln in
QI_WORK_TREE/hello/build-.../hello.sln, select "hello" as startup project, and
start debugging hello_d.exe right away.

.. warning:: If you try to compile hello in release, you’ll get an
  error because "world" has not been compiled in release, so world.lib could not
  found.

Simply run::

  qibuild configure --release world
  qibuild make --release world

And try again.
