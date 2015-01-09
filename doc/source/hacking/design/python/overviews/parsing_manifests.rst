.. _parsing-manifests:

Parsing manifests
=================

How does it work?
-----------------

Things happen in several stages.

Fetching the manifest repository
++++++++++++++++++++++++++++++++

This is done by ``qisrc.sync.fetch_manifest`` method.

We just add the manifest repository to the worktree, using

``qisrc.sync.clone_project``, then reset it to the
branch the user asked us.

We then mark the project has being a manifest project,
so that ``qisrc sync`` called later can now where to find
the manifest XML file


Manifest XML parsing
+++++++++++++++++++++

This is done by ``qisrc.manifest.load`` method.

We parse the XML in order to find every project, read what
branch they need to track, what are there URLs, and whether
or not they are under code review.

If we see them as being under code review, we call
``qisrc.review.setup_project``

Once this is done, we call
``worktree.set_project_review``
so that ``qisrc push`` does not have to parse the manifest again to
see whether or not the project is under code review.

If we see new projects, we add them to the worktree using
``qisrc.sync.clone_project`` and then call
``worktree.set_git_project_config`` so that ``qisrc sync`` does not have to parse the manifest again
to get what is the remote branch we should synchronize with.

