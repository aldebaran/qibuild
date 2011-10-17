Creating a new project
======================

In this tutorial, we will simply create a new project

Navigate to your QI_WORK_TREE and type:

.. code-block:: console

  $ qibuild create foo

Remember, for this to work on windows, you should have:

* Run install-qibuild.bat
* Put C:\Python27 and c:\Python\Scripts in your %PATH%

This will create a new project in QI_WORK_TREE/foo.

Let’s have a look at what has been generated::

  foo
  |__  CMakeLists.txt
  |__  main.cpp
  |__  qibuild.cmake
  |__  qibuild.manifest


* main.cpp is just a standard "Hello World"

* CMakeLists.txt : this is a script file that will be read by CMake to generate
  makefiles, or Visual Studio solutions.

* qibuild.cmake : this file MUST be included by the CMakeLists.txt to find the
  QiBuild CMake framework

* qibuild.manifest : this file MUST be present for QiBuild to know how to build
  the foo project.

If you already have source code somewhere, all you have to do is to:

*  create a qibuild.manifest looking like

.. code-block:: ini

    [project foo]

* copy-paste the qibuild.cmake file from
  qibuild/cmake/qibuild/templates/qibuild.cmake and make sure to include it in
  you root CMakeLists.txt

* (optional, if you want to use qi\_ functions...): include 'qibuild/cmake'
  somewhere

You cand do this by running

.. code-block:: console

  $ qibuild convert

.. note:: 'qibuild convert' will check that your root CMakeLists is correct,
   please read the messages carefully


In any case, the root CMakeLists should look like:

.. code-block:: cmake

  cmake_minimum_required(VERSION 2.8)
  project(my_project)
  include("qibuild.cmake")

The 'project()' call is mandatory for qibuild to work when using
Visual Studio, the include('qibuild.cmake') call must be right
after 'project()', otherwize you can have trouble when cross-compiling.
