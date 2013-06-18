.. _qibuild-contrib:

Contributing to qiBuild
========================

qiBuild development process take place on github:
https://github.com/aldebaran/qibuild


Reporting bugs
--------------

Please open an issue on github for every qibuild bug you may
find, but make sure to read this first:

.. toctree::
    :maxdepth: 1

    reporting_bugs

TODO list
----------

If you want to contribute, but don't know
what to do, you can have a look at the TODO:


.. toctree::
    :maxdepth: 1

    todo

Feel free to just add your own ideas to the list :)


Specifications
+++++++++++++++

This is for items on the TODO that are too large
and require discussion before we start actually
implementing them

.. toctree::
    :maxdepth: 1

    specs/index


Submitting changes
-------------------

Please fork the project on github and make a merge request
if you want to contribute.

Please also read this first:

.. toctree::
   :maxdepth: 1

   cmake/coding_guide
   python/coding_guide

qibuild uses the 'Test Driven Development' technique.

It is advised you write tests **before** adding new code.

You can read more about it here:

.. toctree::
   :maxdepth: 1

   test_driven_development

In any case, you must make sure to check your code is correct
before sending a merge request:

.. toctree::
   :maxdepth: 1

   running_test_suite
   writing_new_tests


Please also make sure to submit documentation
updates concerning your changes.

.. toctree::
   :maxdepth: 1

   writing_documentation
