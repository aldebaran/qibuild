.. _qisrc-tutorial:

Git-to-qisrc cookbook
=====================

Some companies put all their code in one big VCS repository (a lot of them use
Perforce; Facebook and Google use Mercurial).  With Git, this is impractical.

qisrc implements a “meta-” version control system, that allows one to manage a
collection of Git clones in a big "worktree". It offers features similar to the
"one-big-repository" approach, and if you squint really hard, you can think of
the qisrc worktree as a VCS repo.

That means it must be possible to translate Git commands (that you would use if
a project is managed using Git without qisrc) to the equivalent qisrc commands.

For the sake of this comparision, let's suppose that the equivalent of a Git
repository is a qisrc group. This makes sense if we suppose that the point of a
qisrc group is to work on a project, that for some practical reason can not be
kept in only one Git repository.

Let's also suppose that the manifest is stored in the worktree. In the case of
Aldebaran, this means that the worktree must have been created with "-g tools".
If the manifest is not stored in the worktree, you can also have it alongside
your worktree by cloning it with Git.

Download a project
------------------

Git
```

.. code-block:: console

    git clone "git://foo/bar"

qisrc
`````

.. code-block:: console

    qisrc init git@gitlab.aldebaran.lan:qi/manifest.git -g tools -g foo_bar

Create a project
----------------

Git
```

Let's say that we created a repo accessible from the network at
``ssh://git@gitlab.aldebaran.lan/nrubinstein/foobar.git``.

.. code-block:: console

    mkdir foo/bar
    cd foo/bar
    git init
    git commit --allow-empty -m 'first commit'
    git remote add origin git@gitlab.aldebaran.lan:nrubinstein/foobar.git
    git push -u origin master

qisrc
`````

Here, let's create a Git repository and then create a qisrc group containing
only this Git repository. This supposes that you already have a qisrc worktree.

Step 1: create the actual Git repository
::::::::::::::::::::::::::::::::::::::::

Create a Git repository that is accessible from the network, like in the 'Git'
instructions above. Do note that you *need* to create it locally in your qisrc
worktree and to upload a "master" branch. If you do not do this before adding
the Git repository to your worktree, qisrc will break.

Step 2: add the Git repository to the manifest
::::::::::::::::::::::::::::::::::::::::::::::

.. code-block:: console

    cd ../../manifest/default

Edit manifest.xml.

There is a line that says
``<remote name="origin" url="ssh://git@gitlab.aldebaran.lan"/>``.
This means that we will not have to repeat this part of the repo URL.

Create a line that says
``<repo project="nrubinstein/foobar.git" src="foo/bar" remotes="origin"/>``
This tag must be a child of the top-level ``<manifest>`` tag

.. code-block:: console

    git commit -am "Add repository foobar"

Step 3: create a group in the manifest
::::::::::::::::::::::::::::::::::::::

Edit manifest.xml to add your group:

.. code-block:: xml

    <manifest>
      ...
      <groups>
        ...
        <group name="foobar">
          <project name="nrubinstein/foobar.git" />
        </group>

Notice that the group definition uses the (shortened) URL to the Git repository
as seen in the "project" attribute of the "repo" tag, not its path in the
worktree as seen in the "src" attribute of the "repo" tag.

.. code-block:: console

    git commit -am "Create group foobar"

Step 4: push the group
::::::::::::::::::::::

.. code-block:: console

    qisrc push

At Aldebaran, we are using code review for the manifest. That means that the
group is not usable yet. If the push above does not go to code review, you can
skip steps 5 and 6.

Step 5: create a branch
:::::::::::::::::::::::

.. code-block:: console

    git branch foobar
    git push -u origin foobar

Step 6: checkout the branch
:::::::::::::::::::::::::::

.. code-block:: console

    qisrc sync
    qisrc checkout foobar

Step 7: add the group
:::::::::::::::::::::

.. code-block:: console

    qisrc sync
    qisrc add-group foobar

Create a branch
---------------

Git
```

.. code-block:: console

    git checkout -b foo_bar

qisrc
`````

When creating the branch
::::::::::::::::::::::::

Step 1: create the branch in the Git repo that you want to change
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

.. code-block:: console

    cd foo/bar
    git checkout -b foo_bar

Step 2: create the branch in the manifest
'''''''''''''''''''''''''''''''''''''''''

.. code-block:: console

    cd ../../manifest/default
    git checkout -b foo_bar

Then edit manifest.xml: find the line that says
``<repo ... src="manifest/default" />`` and edit it to say ``branch="foo_bar"``.
This is not strictly necessary but will make it easier to edit the branch you
are working on.

Step 3: edit the manifest to switch your repo to your branch
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Edit manifest.xml: find the line that says
``<repo ... src="foo/bar" />`` and edit it to say ``branch="foo_bar"``.

.. code-block:: console

    git commit -am "Create branch foo_bar"
    git push -u origin foo_bar

Step 4: checkout your branch for the whole worktree
'''''''''''''''''''''''''''''''''''''''''''''''''''

.. code-block:: console

    cd ../..
    qisrc sync
    qisrc checkout foo_bar

If everything went well, this last command should do nothing.

Afterwards
::::::::::

Then, everytime you want to change something in a Git repository that you have
not changed yet, you have to reproduce step 1 and 3.

Switch to a branch
------------------

Git
```

.. code-block:: console

    git checkout foo_bar

qisrc
`````

.. code-block:: console

    qisrc checkout foo_bar

When some changes are integrated
--------------------------------

Git
```

When using Git, sometimes you create changes on your foobar branch and at some
point they are integrated in the master branch. Typically, when that happens,
you would remove the foobar branch with:

.. code-block:: console

    git checkout foobar
    git rebase master
    git checkout master
    git branch -d foobar

And then you can remove the remote branch with:

.. code-block:: console

    git push origin :foobar

qisrc
`````

Additionally, when using qisrc, there are two scenarios.

When some changes on some Git repo have been merged to master
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Step 1: Delete the branch in the Git repo
'''''''''''''''''''''''''''''''''''''''''

First, do the Git steps above as you would normally do, but do not remove the
remote branch yet! That would break "qisrc sync" for everyone following your
branch.

Step 2: Edit the manifest
'''''''''''''''''''''''''

.. code-block:: console

    cd ../../manifest/default

Edit manifest.xml: find the line that says
``<repo ... src="foo/bar" branch="foobar" />`` and delete the ``branch="foobar"`` part.

.. code-block:: console

    git commit -am "branch foo/bar of foobar has been merged back to master"
    git push

Step 3: remove the remote branch
''''''''''''''''''''''''''''''''

Now that the manifest is updated, removing the remote Git branch is safe.

.. code-block:: console

    qisrc sync
    cd ../../foo/bar
    git push origin :foobar

Step 4: Checkout your branch for the whole worktree
'''''''''''''''''''''''''''''''''''''''''''''''''''

.. code-block:: console

    cd ..
    qisrc sync
    qisrc checkout foobar

If everything went well, those two commands should not change anything.

When all changes in all Git repos have been merged to master
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

The qisrc manifest branch is useless now, so you can remove it.

.. code-block:: console

    qisrc checkout master
    cd manifest/default
    git push origin :foobar
