.. _parsing-manifests:

Parsing manifests
=================

Introduction - Why do we need manifests?
----------------------------------------

Manifests are here to help you manage several git projects.

The motivation for writing ``qisrc`` was :

- We needed to have a simple way to store the URL of all our git projects

- neither ``git submodule`` nor ``repo`` where good enough for our purposes.


So, what is ``qisrc`` useful for ?

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
      <remote fetch="git@git.aldebaran.lan" />

      <project name="qi/libqi.git" path="lib/libqi" />
      <project name="lib/libnaoqi.git" path="lib/libnaoqi" />
      <project name="gui/choregraphe.git" path="gui/choregraphe" />

    </manifest>


Obviously, you want to be able to put this file under version control,
so you create a git project in ``git@git.aldebaran.lan:qi/manifest.git``
and add this file as a ``default.xml`` file.

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
branch in the manifest repository, and you change the ``default.xml``
file to look like

.. code-block:: xml

   <manifest>
      <remote fetch="git@git.aldebaran.lan" revision="release-1.12" />
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
so you create an other file in the manifest repository called ``doc.xml``,
where you put only the projects you need.


And then, you can use:

.. code-block:: console

    qisrc init git@git.aldebaran.lan:qi/manifest.git -p doc

to clone the required repositories to build the documentation on master.

Of course, if you need to build the doc for the relase, just use:


.. code-block:: console

    qisrc init git@git.aldebaran.lan:qi/manifest.git -p doc -b relase-1.12


But wait, there's more !
++++++++++++++++++++++++

Let's assume you are in a development branch, called ``my_crazy_feature``

You want to rebase ``my_crazy_feature`` with ``master``, and make sure
it stays compatible with every other ``master`` branch on every other project.

So you just run ``qisrc sync``, and:

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

And then to upload changes for review you have to write something like

.. code-block:: console

   git push gerrit master:refs/for/master

With ``qisrc``, all you have to do is to patch the ``default.xml`` to look like:

.. code-block:: xml

   <manifest>
      <remote fetch="git@git.aldebaran.lan" review="http://gerrit:8080" />
      <project name="qi/libqi.git" path="lib/libqi" review="true" />
    </manifest>

And then, ``qisrc sync`` will setup your project for code review, and using
``qisrc push`` will be able to upload your changes for code review.

How does it work?
-----------------

Things happen in several stages.

Fetching the manifest repository
++++++++++++++++++++++++++++++++

This is done by :py:meth:`qisrc.sync.fetch_manifest` method.

We just add the manifest repository to the worktree, using

:py:meth:`qisrc.sync.clone_project`, then reset it to the
branch the user asked us.

We then mark the project has beeing a manifest project,
so that ``qisrc sync`` called later can now where to find
the manifest XML file


Manifest XML parsing
+++++++++++++++++++++

This is done by :py:meth:`qisrc.manifest.load` method.

We parse the XML in order to find every project, read what
branch they need to track, what are there URLs, and wether
or not they are under code review.

If we see them has beeing under code review, we call
:py:meth:`qisrc.review.setup_project`

Once this is done, we call
:py:meth:`worktree.set_project_review() <qisrc.worktree.WorkTree.set_project_review>`
so that ``qisrc push`` does not have to parse the manifest again to
see wether or not the project is under code review.

If we see new projects, we add them to the worktree using
:py:meth:`qisrc.sync.clone_project` and then call
:py:meth:`worktree.set_git_project_config() <qisrc.worktree.WorkTree.set_git_project_config>` so that ``qisrc sync`` does not have to parse the manifest again
to get what is the remote branch we should synchronize with.

