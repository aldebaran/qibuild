qibuild.worktree -- Using a :term:`worktree`
============================================


.. py:module:: qibuild.worktree

qibuild.worktree.WorkTree
-------------------------


.. py:class:: WorkTree(work_tree [,path_hints])

   This class represent a :term:`worktree`

   :param work_tree: The directory to be used as a worktree.
   :param path_hints: Some additional directories to be
                      used when searching for projects.
   :raise: WorkTreeException if two projects have the same name or
                             if two git directories have the same
                             basename.

  .. py:attribute:: buildable_projects

     A ``dict`` {name : Project} of projects found in this worktree

  .. py::attribute:: git_projects

     A ``dict`` {name : path} of git repostories found in this worktree

