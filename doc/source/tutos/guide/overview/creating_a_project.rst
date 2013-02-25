.. _qibuild-create-project:

Creating a new project
======================

In this tutorial, we will simply create a new project

Navigate to your :term:`worktree` and type:

.. code-block:: console

  $ qibuild create foo

Remember, for this to work on windows, you should have:

* Run install-qibuild.bat
* Put ``C:\Python27`` and ``c:\Python27\Scripts`` in your ``%PATH%``.

This will create a new project in ``QI_WORK_TREE/foo``

Let us have a look at what has been generated::

  foo
  |__  qiproject.xml
  |__  CMakeLists.txt
  |__  main.cpp
  |__  test.cpp


* ``main.cpp`` is just a standard "Hello World"

* ``test.cpp`` is a simple test: you use automatic testing, don't you?

* ``CMakeLists.txt`` : this is a script file that will be read by CMake to generate
  makefiles, or Visual Studio solutions.

* ``qproject.xml`` : this file MUST be present for qiBuild to know how to build
  the ``foo`` project.

If you already have source code somewhere, all you have to do is to:

*  create a ``qiproject.xml`` looking like

   .. code-block:: xml

       <project name="foo" />

* (optional, if you want to use qi\_ functions...): include ``find_package(qibuild)``
  somewhere after the call to ``project()``

You can do this by running

.. code-block:: console

  $ qibuild convert

.. note:: 'qibuild convert' will check that your root ``CMakeLists.txt`` is correct,
   please read the messages carefully


In any case, the root ``CMakeLists.txt`` should look like:

.. code-block:: cmake

  cmake_minimum_required(VERSION 2.8)
  project(my_project)
  find_package(qibuild)

The ``project()`` call is mandatory for qibuild to work when using
Visual Studio, the ``find_package(qibuild)`` call must be right
after ``project()``, otherwise you can have trouble when using a toolchain file.
