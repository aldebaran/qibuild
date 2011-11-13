.. _qisrc-manifest-syntax:

qisrc manifest syntax
=====================

General
-------

This file is used by the ``qisrc fetch`` command
to get a list of projects to fecth and add in the
current work tree.


The file should contain on section named ``[project <name>]``
per project, and each section should contain an ``url``
option.

Note: right now, only git URLs are supported.

Example:

.. code-block:: ini

   [project foo]
   url = git://example.com/foo.git

   [project bar]
   url = git@example.com:bar.git

