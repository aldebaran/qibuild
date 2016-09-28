.. _worktree-and-projects:

Worktree and projects
=====================

Every tool is using a worktree.

The WorkTree class contains just a list of paths, which
are simple Project objects. Those do not have a name,
and are identified by there relative path to the worktree.
They are stored in a ``worktree cache``, in
``<worktree root>/.qi/worktree.xml``

::

  <worktree>
  |__ .qi
      |__ worktree.xml
  |__ foo
  |__ bar
      |__ baz

Here for instance you could have two projects: one in ``foo``, and
the other in ``bar``

Projects are added to the worktree with ``qisrc add``, ``qisrc remove``,
but the `

Projects can also contain sub-projects, providing they have
a ``qiproject.xml`` at their root:

.. code-block:: xml

  <!-- in bar/qiproject.xml -->
  <project>
    <project src="baz" />
  </project>



Here, if the ``bar`` path is registered to the worktree and
``bar/baz`` exists, then a project in ``bar/baz`` will be created too


Using the worktree with a qiBuild tool
--------------------------------------

Then, other classes creates their own kind of projects using
the registered paths in the worktree.

For instance, to have a buildable project, you must have

* a ``<qibuild>`` tag in ``qiproject.xml``
* a ``CMakeLists.txt`` file next to the ``qiproject.xml``

So the list of buildable paths (from where you can run CMake)
is always a sublist of all the projects in the worktree.

Buildable projects are then identified by their *names*,
which must be unique in the worktree.

This makes it possible to express dependencies between
buildable projects using just the names, and not caring
where the build projects are actually located on the filesystem


It also means you can nest qibuild and qidoc projects anyway you want.

For instance:

* a build project at the root in :file:`foo`, with the doc in
  :file:`foo/doc`

  .. code-block:: xml

    <!-- in foo/qiproject.xml -->
    <project>
      <qibuild name="foo" />
      <project src="doc" />
    </project>

    <!-- in foo/doc/qiproject.xml -->

    <project>
      <qidoc name="foo" type="shinx" />
    </project>


* Two nested build projects in the same git project (best avoided):

  .. code-block:: xml

    <!-- in top/qiproject.xml -->
    <project>
      <project src="libhello" />
      <qibuild name="helloworld">
        <depends buildtime="true" runtime="true" names="libhello" />
      <qibuild/>
    </project>

    <!-- in top/libhello/qiproject.xml -->
    <project>
      <qibuild name="libhello" />
    </project>

  In this case, the libhello build project lies within the helloworld build
  project (which is at the root in :file:`top`).

  While nested build projects are supported by qibuild, they are best avoided:
  nested build projects complicate mapping between projects and path which
  makes using git log and continuous integration unnecessarilly harder (see
  bellow).


* Two build projects in the same git project, forming
  a "flat hierarchy":

  .. code-block:: xml

    <!-- in top/qiproject.xml -->
    <project>
      <project src="libhello" />
      <project src="helloworld" />
    <project>

    <!-- in top/libhello/qiproject.xml -->
    <project>
      <qibuild name="libhello" />
    </project>

    <!-- in top/helloworld/qiproject.xml -->
    <project>
      <qibuild name="helloworld">
        <depends buildtime="true" runtime="true" names="libhello" />
      <qibuild/>
    </project>

  Note that, while the two build projects are nested within the root
  qiproject, the root one is not a build project, so there is no nested build
  project.

  With this layout, looking at the history of the helloworld project is as
  easy as

  .. code-block:: bash

    cd top
    gitk -- helloworld

  It is easy to setup per-project contiguous integration jobs triggered by
  git commit using path filters.
  Eg. if a commit only changes files in the :file:`libhello` sub-folder,
  the libhello job should be triggered but not the helloworld one.
