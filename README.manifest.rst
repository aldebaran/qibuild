qisrc manifest files
====================

This is a small document describing the state of
qisrc manifests

What we have
-------------


Right now we have several manifests, one for each team.

For instance, ``naoqi`` developers need ``libqi`` and ``linaoqi``,
and ``qimessaging`` developers need ``libqi`` and ``qimessaging``

So we have two manifests:

::

   <!-- naoqi.xml -->
    <feed>
      <project "naoqi"
        url="git@git.aldebaran.lan:naoqi/naoqi.git"
      />

      <project "libqi"
        url="git@git.aldebaran.lan:qi/libqi.git"
      />
    </feed>


    <!-- qimessaging.xml -->
      <feed>
        <project "libqi"
        url="git@git.aldebaran.lan:qi/libqi.git"
      />

      <project "naoqi"
        url="git@git.aldebaran.lan:naoqi/naoqi.git"
      />



Additionally, when we run ``qisrc pull``, we look for the last manifest
used, and try clone new new dependencies

Problems
--------

* The git url of ``libqi`` is duplicated across two files

* Developers can work both on ``naoqi`` and ``qimessaging`` in the same worktree,
  and they may not want to clone ``naoqi`` dependencies when running ``qisrc pull`` from
  ``qimessaging``

* It's hard to attach a manifest URL with several repositories: some repositories can
  belong to several manifests, and so on

* The information is redundant with the build dependencies. ``naoqi`` project already has
  something like

::

    <project name="naoqi">
      <depends names="libqi" />
    </project>


A wrong solution
----------------

Just for reference, a solution we used to have was to put the URL of the dependencies
inside the configuration of the projects.

This is bad because:

* url of projects are duplicated across *many* config files
* url are hard-coded so you cannot easily mirror the project


A better solution
------------------


So it seems a good solution would be to have a global manifest to track
**every** known git project.

Then, ``qisrc pull`` can recursively parse the build dependencies,
try to find them inside the global manifest, and clone the dependencies.


New manifest format
--------------------

Manifest will look like the one used by repo, but not be the same ...

::

  <!-- default.xml -->
  <manifest>

    <remote name="origin"
            fetch="git@git.aldebaran"
            review="http://git.aldebaran.lan:8080'
    />


    <project name="qi/libqi"
             path="lib/libqi"
             review="true"
    />


    <project name="qi/qibuild"
             path="tools/qibuild"
             review="true"
    />

  </manifest>


Like repo, the manifest itself will be in a git repository.

(git@git.aldebaran.lan:qi/manifest.git)

It will contain *everything*.

If anyone adds a new repo here, it becomes available on every build farm
and on every desktop.

I don't believe it is useful for hal developers not to have choregraphe.

Local config file for qibuild projects
--------------------------------------


It's quite useless to parse the worktree everytime to find the project, which projects are
in a git repository.

Also, aldeb-templates for instance is only used by qidoc so it has a ``qiproject.xml`` but
no CMake file, so ``qc`` fails if it goes through aldeb-templates...

But, let's not forget that in some cases, some git repositories will contain several
``qiproject.xml`` files

So qibuid should maintain a local config file, looking like this::

  <!-- QI_WORK_TREE/.qi/worktree.xml -->
  <worktree>

    <project name="libqi"
      src="lib/libqi"
    />

    <project name="aldeb-templates"
      src="doc/templates"
      buildable="false"
    />

    <project name="narrateur-gui"
      src="narrateur/gui"
      git="narrateur"
    />

    <project name="narrateur-lib"
      src="narrateur/lib"
      git="narrateur"
    />

    <project name="narrateur"
      src="narrateur"
      buildable="false"
    />

    <manifest
      url="git@git.aldebaran.lan:qi/manifest.git"
    />

  </worktree>


We assume every buildable project is at the root of the git project,
unless the ``git`` attribute says otherwize.


qisrc command line API
-----------------------


* qisrc fetch -> gone
* qisrc pull -> gone

* qisrc init -> new mandatory argument: qisrc init MANIFEST_URL

* qisrc sync -> new command

  * look for the manifest in ``.qi/worktree.xml``
  * clone the manifest repo
  * parse the default.xml in the manifest repo
  * clone new project
  * parse new project to look for new qibuild projects
  * update ``.qi/worktree.xml``
  * for each git project:
    * run git pull or git pull --rebase (maybe something smarter later)


* qisrc review:

  * Add hook from gerrit if not already there
  * Push the commit to gerrit

* qisrc grep : just because it exists in repo :)

Python API
----------

Work in progress. Not sure about keeping the Worktree / Toc classes.

Also, we need to remove the duplication between:

* solving deps in qisrc pull   (where we pull only the deps)
* solving deps in qidoc build  (where we also want to be able to use
  -s, guess current project from worktree, and all that jazz)

