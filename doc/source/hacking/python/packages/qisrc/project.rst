qisrc.project - git projects in a GitWorkTree
==============================================

.. py:module:: qisrc.project

qisrc.worktree.GitProject
--------------------------

.. py:class:: GitProject

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
