.. _qibuild-overview:

What is qibuild
===============

qiBuild aims to make compilation of your sources easy. It manages dependencies
between projects and supports cross-compilation.

By default qiBuild uses libraries provided by your system, but you can also use
qiToolchain to manage sets of pre-compiled packages (called toolchains) if you
want. Cross-compilation is then just a matter of using a specific toolchain.

qiBuild is truly cross-platform: it is tested on Linux, Mac and Windows. Being
based on the well-known CMake build system, it allows you to use your existing
tools such as gcc, Make, or Visual Studio.

The qiBuild framework tries hard to stand out of your way: it remains close to
standards, and will play nice with other build systems.

qiBuild is composed of two parts:

* the qiBuild CMake framework, that simplifies authoring CMakeLists.txt.

* the qibuild/qitoolchain command line tools, that helps build projects while
  taking dependencies into account and generate re-distributable binary
  packages


Is qibuild the only one build framework
=======================================

Of course not!

You can have a loot at

.. toctree::
   :maxdepth: 1

   other/cmake
   other/rosbuild
   other/qmake
   other/autotools
