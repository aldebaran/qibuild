qisys.worktree -- Using a :term:`worktree`
============================================


.. py:module:: qisys.worktree

qisys.worktree.WorkTree
-------------------------


.. autoclass:: WorkTree

  .. automethod:: WorkTree.__init__


  .. py:attribute:: root

     The root of the work tree.

  .. py::attribute:: projects

     A list of projects found is this worktree, as
     read from ``.qi/worktree.xml``

  .. py:attribute:: buildable_projects

     A list of projects found in this worktree that
     are buildable (They should have a ``qiproject.xml`` and
     a ``CMakeLists.txt`` at their top directory)

  .. py:attribute:: git_projects

     A list git repositories found in this worktree

  .. automethod:: get_project

  .. automethod:: add_project

  .. automethod:: remove_project

  .. automethod:: set_git_project_config

  .. automethod:: set_project_review

