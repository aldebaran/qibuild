qisrc.manifest -- Parsing manifest files
=========================================

.. automodule:: qisrc.manifest

.. seealso::

   * :ref:`qisrc-manifest-syntax`

qisrc.manifest.load
-------------------

.. autofunction:: load

qisrc.manifest.Manifest
-----------------------

.. autoclass:: Manifest

  .. py:attribute:: remotes

     A list of :py:class:`Remote` objects

  .. py:attribute:: projects

     A list of :py:class:`Project` objects

qisrc.manifest.Remote
---------------------

.. autoclass:: Remote

  .. py:attribute:: name

      Name of the remote (default is 'origin')

  .. py:attribute:: fetch

     URL of the remote (for instance: git://example.com)

  .. py:attribute:: revision

     Branch to fetch by default (default is 'master')

  .. py:attribute:: review

     URL of the review server (for instance: http://gerrit:8080)

qisrc.manifest.Project
----------------------

.. autoclass:: Project

  .. py:attribute:: name

     Name of the project. Will be joined with the remote
     URL  (if remote is ``git@foo.com``, and name is ``bar/baz.git``,
     final git URL will be ``git@foo.com:bar/baz.git``)

  .. py:attribute:: path

     Relative path in which to clone the project

  .. py:attribute:: review

     Wether the project is under code review

  .. py:attribute:: remote

     The remote in which to read the URL ('origin' by default)

  .. py:attribute:: revision

     The branch to clone and track  (the one from the matching remote by
     default)

  .. py:attribute:: fetch_url

     URL to be fetched

  .. py:attribute:: review_url

     URL to which we should upload the new changes
