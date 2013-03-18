qisrc.worktree -- Managing git projects
=======================================


.. py:module:: qisrc.worktree


qisrc.worktree.GitWorkTree
--------------------------

.. autoclass:: GitWorkTree
    :members:


qisrc.worktree.GitProject
--------------------------

This class represent a git configuration.

Every git configuration is stored in the worktree, in a
``.qi/git.xml`` file.

``qisrc`` then make sure the actual git repository matches the configuration stored
in the file.  (That the branches and remotes exist, and the tracking branches
are correctly set)

``qisrc sync`` also reads the configuration from the remote manifest, and makes sure
everything matches

.. autoclass:: GitProject
    :members:

qisrc.worktree.Remote
---------------------

.. py:class:: Remote

    A remote, as stored in the ``.qi/git.xml`` file

    .. py:attribute:: name

      The name of the remote

    .. py:attribute:: url

      The url  of the remote
      Note that in case of a ``gerrit`` repository, this will be
      the public, ``http://`` url, ``qisrc push`` making sure we
      use the ``ssh url`` when uploading patch sets.

    .. py:attribute:: review

      Wether the remote supports code review.
        return res

qisrc.worktree.Branch
----------------------

.. py:class:: Branch

  .. py:attribute:: name

    The name of the branch

  .. py:attribute:: tracks

    The name of the remote tracked by this
    branch

  .. py:attribute:: remote_branch

    The name of the remote branch tracked by
    this branch. Default is a remote with the same
    name

  .. py:attribute:: default

     Wether this is the default branch.
     ``qisrc sync``, will try to synchronize
     this branch by default
