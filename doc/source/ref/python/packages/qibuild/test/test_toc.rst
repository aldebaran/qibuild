qibuild.test.test_toc
=====================

.. py:module:: qibuild.test.test_toc

TestToc object
--------------

.. autoclass:: TestToc
   :members:

A class to compile the projects in ``python/qibuild/test``

Example:

.. code-block:: python

    from qibuild.test.test_toc import TestToc


    def test_hello_compiles():
        with TestToc() as toc:
            hello = toc.get_project("hello")
            toc.configure_project(hello)
            toc.build_project(hello)

.. warning:: The tests written in this module are very old (but still useful)
             Feel free to rewrite them, but please do NOT add new tests
             in this module.

