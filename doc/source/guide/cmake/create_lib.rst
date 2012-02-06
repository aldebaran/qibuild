.. _cmake-create-lib:

Creating a library
==================

This tutorial only convers the most simple way of writing a library.

If you are working in a large project, or wish to re-distribute your library,
you may want to read this more in-depth tutorial: :ref:`how-to-write-a-library`

Requirements
------------

We assume you have a qiBuild project containing a executable named ``foo``.

You can use ``qibuild create foo`` to get such a project.

We are going to write a function called ``get_answer()`` that will return an
integer.

Since this function may be used by other people, we are going to put it in a
library, called answer

The answer library
------------------

Add the following files into your project:

.. code-block:: cpp

  // answer.h

  ///
  /// Get the meaning of life
  ///
  int get_answer();

.. code-block:: cpp

  // answer.cpp

  #include "answer.h"

  int get_answer()
  {
    return 42;
  }

Then, edit main.cpp to have:

.. code-block:: cpp

  #include <stdio>
  #include "answer.h"

  int main()
  {
    std::cout << "The answer is: " << get_answer() << std::endl;
    return 0;
  }

Using the answer library
------------------------

In order to use our library in the foo executable, we have to:

* Find the ``answer.h`` file : so we need to add some include directories

* Create a library named answer with ``answer.h`` and ``answer.cpp``

* Link the ``foo`` executable with the ``answer`` library.

Adding the include directories
++++++++++++++++++++++++++++++

Add the following line to the CMakeLists.txt:

.. code-block:: cmake

  include_directories(".")

.. note:: CMake always interprets paths relative to the current CMakeLists file
   So since the CMakeLists and your headers are in the same directory,
   include_directories(".") is enough

Creating the answer library
+++++++++++++++++++++++++++

Add a call to :cmake:function:`qi_create_lib`:

.. code-block:: cmake

  qi_create_lib(answer answer.h answer.cpp)

This creates a static library by default, named ``libanswer.a`` on UNIX, and
``answer.lib`` or ``answer_d.lib`` on Windows.

It also makes the ``answer`` library usable by other targets.

Link the foo executable with the answer library
+++++++++++++++++++++++++++++++++++++++++++++++

Add a call to :cmake:function:`qi_use_lib`:

.. code-block:: cmake

  qi_use_lib(foo answer)

Make sure you call this after the call to :cmake:function:`qi_create_lib` - you need to create a
library before using it.

This call does several things:

* It adds a dependency between the ``answer`` library and the ``foo`` executable

* It makes sure the ``foo`` executable is linked with the ``answer`` library

Building
--------

You can then build your project.

A few notes:

* On Windows, the library will be found in ``build/sdk/lib/answer_d.lib`` if
  built in debug, or in ``build/sdk/lib/answer.lib`` if built in release.

* On linux, the library will be found in ``build/sdk/lib/libanswer.so``

* On mac, the library will be fon in ``build/sdk/lib/libanswer.dylib``

.. note:: On UNIX, you can force the creation of static library by using
   -DBUILD_SHARED_LIBS=OFF

On Windows, the sources need to be patched to use ``answer`` as a shared
library, but this out of the scope of this documentation.


Conclusion
----------

The final CMakeLists.txt code looks like

.. code-block:: cmake

  cmake_minimum_required(VERSION 2.8)
  find_package(qibuild)
  project(foo)

  include_directories(".")
  qi_create_lib(answer answer.h answer.cpp)
  qi_stage_lib(answer)

  qi_create_bin(foo main.cpp)
  qi_use_lib(foo answer)



