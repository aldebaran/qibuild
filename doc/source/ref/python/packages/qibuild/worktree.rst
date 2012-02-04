qibuild.worktree -- Using a :term:`worktree`
============================================


.. py:module:: qibuild.worktree

qibuild.worktree.WorkTree
-------------------------


.. autoclass:: WorkTree

  .. automethod:: WorkTree.__init__


  .. py:attribute:: work_tree

     The root of the work tree.

  .. py:attribute:: buildable_projects

     A ``dict`` {name : Project} of projects found in this worktree
     Initialized with

  .. py:attribute:: git_projects

     A ``dict`` {name : path} of git repostories found in this worktree

Other functions in this module
------------------------------

qibuild.worktree.worktree_open
+++++++++++++++++++++++++++++++

.. autofunction:: qibuild.worktree.worktree_open

Typical usage from an action is:

.. code-block:: python

    # To handle --work-tree option
    def configure_parser(parser):
        qibuild.worktree.work_tree_parser(parser)

    def do(args):
        qiwt = qibuild.worktree_open(args.work_tree)
