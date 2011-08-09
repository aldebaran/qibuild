.. QiBuild documentation master file, created by
   sphinx-quickstart on Mon Aug  1 15:48:52 2011.

Welcome to QiBuild's documentation!
===================================


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

* the qibuild/qitoolchain command line tools, that help build projects while
  taking dependencies into account.

References
----------

.. toctree::
   :maxdepth: 2

   cmake/index

   man/index


* :ref:`List of qibuild cmake functions <genindex>`

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
