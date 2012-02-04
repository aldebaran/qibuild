

.. toctree::
  :hidden:

  getting_started
  qibuild_in_five_minutes
  ref/index
  guide/index
  contrib/index
  design/index
  other_build_frameworks
  relnotes


.. _qibuild-documentation:

qiBuild documentation
=====================


Introduction
------------

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

Getting started with qiBuild
----------------------------

First, please follow the tutorial in the :ref:`qibuild-getting-started` section.

You can now read the :ref:`qibuild-in-five-minutes` section if you want to dig
in right now.

qiBuild programming guide
--------------------------


Please follow the :ref:`qibuild-guide` for a more progressive, comprehensive course.


References
----------

* :ref:`qibuild-cmake-api`
* :ref:`qibuild-python-doc`

Man pages
+++++++++

* :ref:`qibuild <qibuild-man-page>`
* :ref:`qisrc <qisrc-man-page>`
* :ref:`qitoolchain <qitoolchain-man-page>`

Configuration syntax
++++++++++++++++++++

* :ref:`qibuild-xml-syntax`
* :ref:`qiproject-xml-syntax`
* :ref:`toolchain-feed-syntax`
* :ref:`qisrc-manifest-syntax`



Contributing to qiBuild
------------------------

qiBuild development process take place on github:
https://github.com/aldebaran/qibuild

Please fork the project on github and make a merge request
if you want to contribute.

Please also read this first:

.. toctree::
   :maxdepth: 1

   contrib/cmake/coding_guide
   contrib/python/coding_guide

Make sure you check your code is correct
before sending a merge request

.. toctree::
   :maxdepth: 1

   contrib/running_test_suite


Please also make sure to submit documentation
updates concerning your changes.

.. toctree::
   :maxdepth: 1

   contrib/writing_documentation


qiBuild design
--------------

Read this if you want to learn more about qiBuild design:

:ref:`qibuild-design`


qiBuild and other build frameworks
----------------------------------

Read this if you are already using a build framework.

* :ref:`qibuild-compared-to-other-build-frameworks`


Release notes
-------------

* :ref:`qibuild-relnotes`
