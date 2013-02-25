.. _qibuild-contrib:

Contributing to qiBuild
------------------------

qiBuild development process take place on github:
https://github.com/aldebaran/qibuild

Please open an issue on github for every qibuild bug you may
find, but make sure to read this first:

.. toctree::
    :maxdepth: 1

    reporting_bugs

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


Please also make sure to submit documentation
updates concerning your changes.

.. toctree::
   :maxdepth: 1

   writing_documentation

If you are using qibuild from the git repository,
have a look at the :ref:`qibuild-cooking` section
first.

.. toctree::
   :hidden:

   reporting_bugs
   cmake/coding_guide
   python/coding_guide
   cooking
   writing_new_tests
