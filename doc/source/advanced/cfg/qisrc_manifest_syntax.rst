.. _qisrc-manifest-syntax:

qisrc manifest syntax
=====================

General
-------

This file is used by the ``qisrc init`` command
to get a list of projects to fetch and add in the
current work tree.


.. warning:: Right now, only git URLs are supported.


An minimal example may be

.. code-block:: xml

    <manifest>
      <remote fetch="git://example.com" />
      <project name = "foo/bar.git" path="bar" />
    </manifest>


Here the repository from ``git://example/foo/bar.git`` will be cloned
into ``QI_WORTREE/bar``


manifest node
-------------

The ``manifest`` node accepts two types of children

  * ``remote`` node
  * ``project`` node


remote node
------------

The ``remote`` node *must* have a ``fetch`` attribute, that will
be used as a base URL for every project.

You can have several remotes with different names, like this:

.. code-block:: xml

  <manifest>
    <remote name="public" fetch="git://github.com" />
    <remote name="origin" fetch="git@git.aldebaran.com" />
    <project
      name="aldebaran/qibuild.git"
      path="tools/qibuild"
      remote="public" />
    <project
      name="naoqi/naoqi.git"
      path="naoqi"
    />
  </manifest>

* ``git@git.aldebaran.com:naoqi/naoqi.git`` will be cloned into ``naoqi``,
   (because the default remote is ``public``)

* `git://github.com/aldebaran/qibuild.git`` will be cloned into ``tools/qibuild``.


project node
------------

The ``project`` node *must* have a ``name`` attribute.

If ``path`` is not given, it will deduced from the ``name``

(for instance the ``foo/bar.git`` will be cloned to ``foo/bar``.

If ``review`` is true, you must have a ``review`` attribute in the matching remote:

The ssh git url will be decuded from the gerrit server url:

.. code-block:: xml

   <manifest>
      <remote
        fetch="git@foo.com"
        review="http://gerrit:8080"
      />
      <project name="bar/baz.git" review="true"
    </manifest>


Here ``qisrc init`` will try to create an ssh connection with
``git://<username>@gerrit:29418``, where ``username`` is read from the
operating system first, or asked to the user.

.. seealso::

   * :ref:`parsing-manifests`
