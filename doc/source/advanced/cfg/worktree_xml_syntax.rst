.. _worktree-xml-syntax:

worktree.xml configuration file syntax
======================================

General
--------

Contrary to ``.qi/qibuild.xml``, this file is not supposed to
be edited by the user.

It can be seen more as a database to store the projects sources.

One of the most recurring complains about ``qibuild 1.14`` is that
it spent to much time just exploring the worktree to find the projects,
making it hard to write a tool such as ``qicd`` which would be
fast enough.

The manifest right now only contains ``project`` nodes.

Example
--------

Let's asume you have a manifest.xml like this:

.. code-block:: xml

  <manifest>
    <remote fetch="git@example.com" />

    <project name="thirdparty/tinyxml.git" path="lib/tinyxml" />
    <project name="foo/foo.git" path="lib/foo" review="true"/>
   </manifest>


Here's what the ``worktree.xml`` will look like after
``qisrc init`` :

.. code-block:: xml


  <worktree>
    <project manifest="true" profile="default" src="manifest/default" />
    <project branch="master" remote="origin" src="lib/tinyxml" />
    <project branch="master" remote="origin" review="true" src="lib/foo" />
  </worktree>


project node
------------

The ``project`` node can be of several types

manifest project
+++++++++++++++++

Just a hint to tell ``qisrc`` where the ``manifest`` repository has been
cloned, and what is the profile to use.

.. seealso::

   * :ref:`parsing-manifests`

The manifest ``project`` should have the following attributes:

* ``src`` the path to the sources of the manifest, relative to the :term:`worktree` root.

* ``profile`` the profile of the manifest to use, so that the call to
  ``qisrc sync`` knows what profile to use.

project
+++++++

The ``manifest`` project should have the following attributes:

* ``review`` : a boolean to see if the project is under code review, so that
  ``qisrc push`` can complain if the project is NOT under code review, rather
  than complaining that the ``gerrit`` remote does not exits.

* ``src`` : the path to the sources of the project, relative to the :term:`worktree` root.

* ``branch``, ``remote`` : the remote to track, and the branch to synchronize. Used by
  ``qisrc sync``. We assume the remote has been created correctly by ``qisrc init``

