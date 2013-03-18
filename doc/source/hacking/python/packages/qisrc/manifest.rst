qisrc.manifest -- Parsing manifest files
=========================================

.. automodule:: qisrc.manifest

.. seealso::

   * :ref:`qisrc-manifest-syntax`

qisrc.manifest.Manifest
-----------------------

.. autoclass:: Manifest
    :members:

qisrc.manifest.RepoConfig
-------------------------

.. autoclass:: RepoConfig

  .. py:attribute:: remote

      a ``Remote`` object

  .. py:attribute:: src

      the relative path where this repository should
      be cloned in the worktree

  .. py:attribute:: project

      the name of the git project, the full url will
      be computed by joining the remote url and the
      project name

  .. py:attribute:: default_branch

      the default branch of this project. Should match
      a branch in the remote

  .. py:attribute:: remote_url

      Computed during parsing

  .. py:attribute:: review

      wether the project is under code review.
      Set during parsing


