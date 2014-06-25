.. _qisrc-tutorial:

Managing git projects with qisrc
================================

Introduction
------------

The motivation for writing ``qisrc`` was :

* We needed to have a simple way to store the URL of all our git projects

* Neither ``git submodule`` nor ``repo`` were good enough for our purposes.
  (git submodules are tricky to use, ``repo`` is nicer but leaves your
  git worktrees in a strange state)


Installation
------------

Requirements
++++++++++++

First make sure that ``qiBuild`` is installed correctly.
(see :ref:`getting-started`)

Open a console and type

.. code-block:: console

  qibuild --version

Install git
++++++++++++

See the ``github`` documentation for the details.

Tutorial
---------

Let's assume you have several git projects
This is actually what roughly happens for Aldebaran.

* An open source project called ``libqi``
* A closed source library called ``libnaoqi``, containing libraries you
  want provide a C++ SDK for.
* A proprietary software called ``choregraphe``

Have a fixed layout in every worktree
+++++++++++++++++++++++++++++++++++++++

- ``qisrc`` lets you have your projects in whatever layout you want.
  For instance, you may want to always have libraries in ``lib/`` ,
  and the GUIs in ``gui``, so you want to make sure everyone has a layout
  like this::

    lib/
        libqi
        libnaoqi
    gui/
        choregraphe

Doing so is easy: just write a manifest looking like

.. code-block:: xml

   <manifest>
      <remote name="origin" url="git@git.aldebaran.lan" />

      <repo project="qi/libqi.git"        src="lib/libqi" />
      <repo project="lib/libnaoqi.git"    src="lib/libnaoqi" />
      <repo project="gui/choregraphe.git" src="gui/choregraphe" />

    </manifest>


Obviously, you want to be able to put this file under version control,
so you create a git project in ``git@git.aldebaran.lan:qi/manifest.git``
and add this file as a ``manifest.xml`` file.

And then, running:

.. code-block:: console

    qisrc init git@git.aldebaran.lan:qi/manifest.git


Just works and lets you checkout every project you need to compile choregraphe,
in the correct layout.


Handling release branches
+++++++++++++++++++++++++


``qisrc`` makes it easy to have several projects all tracking the same branch.

For instance, when doing a choregraphe release, you may want to make sure everything
is in the ``release-1.12`` branch

So you create a ``release-1.12`` branch on every repository, then a ``release-1.12``
branch in the manifest repository, and you change the ``manifest.xml``
file to look like

.. code-block:: xml

   <manifest>
      <remote url="git@git.aldebaran.lan" branch="release-1.12" />
    </manifest>


And then, running:

.. code-block:: console

    qisrc init git@git.aldebaran.lan:qi/manifest.git -b release-1.12


automatically clones every project you need, with a nice 'release-1.12'
local branch ready to track the 'release-1.12' remote branch.

Of course, since you have created a branch inside the manifest, it is
easy to add new repositories just for master.


Handling profiles
+++++++++++++++++

You may then want to build the documentation of ``libqi`` and ``libnaoqi``,
while making sure the sources of ``choregraphe`` never leak.

Also, the people only working on the documentation don't need to clone everything,
so you create an group in the manifest file where you put only the projects you need.

.. code-block:: xml

  <manifest>
    ...
    <groups>
      <group name="doc" />
        <project name="libqi" />
        <project name="libnaoqi" />
      </group>
    </groups>

  </manifest>

And then, you can use:

.. code-block:: console

    qisrc init git@git.aldebaran.lan:qi/manifest.git --group doc

to clone the required repositories to build the documentation on master.

Of course, if you need to build the doc for the release, just use:


.. code-block:: console

    qisrc init git@git.aldebaran.lan:qi/manifest.git --group doc --branch relase-1.12


But wait, there's more !
++++++++++++++++++++++++

Let's assume you are in a development branch, called ``my_crazy_feature``

You want to rebase ``my_crazy_feature`` with ``master``, and make sure
it stays compatible with every other ``master`` branch on every other project.

So you just run ``qisrc sync --rebase-devel``, and:

* The manifest you clone inside your worktree is updated
* Every projects that were added to the manifest/default.xml file are
  cloned to your worktree.
* For each project, ``qisrc sync`` called ``git pull --rebase`` if you are
  on the ``master`` branch
* For the project you are currently working in, ``qisrc sync`` sees that
  you are not on the correct branch, but your local ``master`` branch can be
  fast-forwared to ``origin/master``. So it just does that, and then
  put you back to your ``my_crazy_feature`` branch, ready to continue working
  or just do something like ``git rebase master``


Handling code review
++++++++++++++++++++


If you are using gerrit, you have to do two manual commands before being able
to push the results under code review:

* Add a remote in order to be able to push the changes

.. code-block:: console

   git remote add gerrit ssh://john@gerrit:29418/lib/libqi.git

* Get a hook so that your commits all get a ChangeID:

.. code-block:: console

   scp -P 29418 john@gerrit:hooks/commit-msg .git/hooks

And then to upload changes for review you have run something like

.. code-block:: console

   git push gerrit master:refs/for/master

You can get ``qisrc`` to perform these operations for you, by adding a
new ``gerrit`` remote to the ``manifest.xml`` file:

.. code-block:: xml

   <manifest>
      <remote name="origin" url="git@git.aldebaran.lan" />
      <remote name="gerrit" url="ssh://gerrit.aldebaran.lan:29418" />
      <project name="qi/libqi.git" path="lib/libqi" remotes="origin gerrit" />
    </manifest>

And then, ``qisrc sync`` will setup your project for code review, and using
``qisrc push`` will be able to upload your changes for code review.

Handling several remotes
++++++++++++++++++++++++

This is useful when you have a fork of an upstream project, and want to
keep a reference to the upstream url.

.. code-block:: xml

  <manifest>
    <remote name="origin" url="git@example.com" />
    <repo project="foo/bar.git" src="lib/bar" remotes="origin">
      <upstream name="my-upstream" url="git@somewhereelse.org" />
    </repo>
  </manifest>

This will create a remote called ``my-upstream`` with the ``git@somewhereelse.org`` url.
