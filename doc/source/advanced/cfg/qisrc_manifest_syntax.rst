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
      <remote name="origin" url="git://example.com" />
      <repo project="foo/bar.git" remotes="origin" src="bar" />
    </manifest>


Here the repository from ``git://example.com/foo/bar.git`` will be cloned
into ``QI_WORTREE/bar``


manifest node
-------------

The ``manifest`` node accepts three types of children

* ``remote`` node
* ``repo`` node
* ``groups`` node


remote node
------------

The ``remote`` node *must* have a ``url`` attribute, that will
be used as a base URL for every project.

You can have several remotes with different names, like this:

.. code-block:: xml

  <manifest>
    <remote name="public" url="git://github.com" />
    <remote name="origin" url="ssh://git@git.aldebaran.com" />
    <repo
      project="aldebaran/qibuild.git"
      src="tools/qibuild"
      remotes="public"
    />
    <repo
      project="naoqi/naoqi.git"
      src="naoqi"
    />
  </manifest>

* ``ssh://git@git.aldebaran.com/naoqi/naoqi.git`` will be cloned into ``naoqi``,
  (because the default remote is ``origin``)

* ``git://github.com/aldebaran/qibuild.git`` will be cloned into ``tools/qibuild``.
  (because ``public`` is used as remote)

Many types of url are supported:

* ``file://``
* ``http://``
* ``git://``
* ``ssh://<username>@<host>`` when using ssh
* ``ssh://<username>@<host>:<port>`` when using ssh on a non-standard port


Additionally, if you are using gerrit with ssh, you can specify that
the remote will be used for code review (this is useful to change
``qisrc push`` behavior, so that changes are pushed to ``refs/for/master``
).



.. code-block:: xml

  <manifest>
    <remote name="gerrit" url="ssh://review.corp.com:29418" review="true"/>
  </manifest>


Since when using gerrit, you have several usernames,
the username is asked by ``qisrc`` when the manifest is parsed.

repo node
---------

The ``repo`` node *must* have a ``project`` attribute.

It also *must* have a ``remotes`` attribute matching some existing
``remote`` nodes.

If ``src`` is not given, it will deduced from the project name.
(for instance the ``foo/bar.git`` repo will be cloned to ``foo/bar``)


.. code-block:: xml

   <manifest>
      <remote name="origin" url="git://example.com" />
      <remote name="gerrit" url="ssh://review.corp.com:29418" review="true" />
      <project name="bar/baz.git" remotes="origin gerrit" />
    </manifest>


Here ``qisrc init`` will try to create an ssh connection with
``ssh://<username>@review.corp.com:29418``, where ``username`` is read from the
operating system first, or asked to the user.

The repository will be configured with two remotes: ``origin``, and ``gerrit``,
and the ``commit-msg`` gerrit hook will be fetched automatically from
``<username>@<server>:hooks/commit-msg`` on the given port .



groups node
-----------

Groups nodes *must* have a ``name`` attribute.
Then they contain a list of project name, and can include other groups.

.. code-block:: xml

  <groups>
    <group name="testing">
      <project name="gtest.git" />
      <project name="gmock.git" />
    </group>
    <group name="core">
      <group name="testing" />
      <project name="libcore" />
    </group>
  </groups>

Here we've defined a group named "testing", so that it's easy to
get the ``gtest`` and ``gmock`` repositories together.

If someone uses ``qisrc inint --group core``, he will get ``gtest``, ``gmock`` and
``libcore``.

.. seealso::

   * :ref:`parsing-manifests`
