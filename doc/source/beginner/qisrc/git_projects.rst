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

      <repo project="qi/libqi.git"        remotes="origin" src="lib/libqi" />
      <repo project="lib/libnaoqi.git"    remotes="origin" src="lib/libnaoqi" />
      <repo project="gui/choregraphe.git" remotes="origin" src="gui/choregraphe" />

    </manifest>


Obviously, you want to be able to put this file under version control,
so you create a git project in ``git@git.aldebaran.lan:qi/manifest.git``
and add this file as a ``manifest.xml`` file.

And then, running:

.. code-block:: console

    qisrc init git@git.aldebaran.lan:qi/manifest.git


Just works and lets you checkout every project you need to compile Choregraphe,
in the correct layout.


Handling release branches
+++++++++++++++++++++++++


``qisrc`` makes it easy to have several projects all tracking different branches.

For instance, when doing a Choregraphe release, you may want to make sure everything
is in the ``release-1.12`` branch

So you create a ``release-1.12`` branch on every repository, then a ``release-1.12``
branch in the manifest repository, and you change the ``manifest.xml``
file to look like

.. code-block:: xml

   <manifest>
      <remote name="origin" url="git@git.aldebaran.lan" />
      <repo project="qi/libqi.git" remotes="origin" branch="release-1.12" />
      ...
    </manifest>


And then, running:

.. code-block:: console

    qisrc init git@git.aldebaran.lan:qi/manifest.git -b release-1.12


automatically clones every project you need, with a nice 'release-1.12'
local branch ready to track the 'release-1.12' remote branch.

Of course, since you have created a branch inside the manifest, it is
easy to add new repositories just for master.

If you do not want to create a new worktree, you can also use:

.. code-block:: console

    qisrc checkout release-1.12


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


You can also list, add and remove the groups used in your worktree by using
``qisrc list-groups``, ``qisrc add-group``, ``qisrc rm-group``


Handling development branches
+++++++++++++++++++++++++++++

Let's say you have two branches for every project in your worktree
(and thus two branches in your manifest repo)

``master``, which is a stable branch, and ``next``, where development occurs.
Bug fixes may be submitted on ``master`` directly, so you may want to make
sure ``next`` is always up to date, by rebasing ``next`` on top of ``master``.

To do so, in a worktree configured with the ``next`` branch of the manifest,
use:

.. code-block:: console

    qisrc rebase master

If you are happy with the changes, you can also run:

.. code-block:: console

    qisrc rebase master --push

(Since this command uses ``git push --force``, use this at your own risk)


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
