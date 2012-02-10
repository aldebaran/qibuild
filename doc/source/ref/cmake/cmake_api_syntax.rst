.. _cmake-api-syntax:

CMake API syntax
================

First, you have to understand how CMake parses functions calls.

.. code-block:: cmake

   function(foo spam)

   endfunction()


Here you must call ``foo`` with at least one argument, that will be
referenced as ``spam`` in the body of the function.

But if you call ``foo`` with more arguments, they will simply stored
in a variable called ``${ARGN}``

There are three kind of keywords you can find in the ARGN list:

* flags: their presence will trigger a different behavior for the function
  (For instance, the ``NO_INSTALL`` keyword of :cmake:function:`qi_create_lib`)
  In the signature of the function, they appear like this::

    [NO_INSTALL]

* parameter: the immediately following argument will be read.
  (For instance, the ``SUBFOLDER`` keyword of :cmake:function:`qi_create_lib`)
  In the signature of the function, they appear like this::

    [SUBFOLDER <subfolder>]

* groups: the following arguments will be parsed until a keyword is found.
  (For instance, the ``SRC`` keyword of :cmake:function:`qi_create_lib`)

  In the signature of the function, they appear like this::

    [SRC <src> ...]

Lastly, it is possible you will have *unparsed* arguments at then end of your call.
For instance, you could use ``qi_create_lib`` like this:

.. code-block:: cmake

    qi_create_lib(foo STATIC SUBFOLDER bar foo.cpp foo.hpp)


Here the ``STATIC`` and ``SUBFOLDER`` keyword have been parsed, to the
remaining arguments are ``foo.cpp`` and ``foo.hpp``.

In the signature of the function, they appear like this::

  [<remain args> ...]


Most of the qi functions to create targets merge the ``SRC`` group with the
remaining arguments, so their is no difference between

.. code-block:: cmake

    qi_create_lib(foo SRC foo.cpp foo.hpp)

and

.. code-block:: cmake

   qi_create_lib(foo foo.cpp foo.hpp)




