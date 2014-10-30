.. _qidoc-tutorial:

Building documentation with qidoc
=================================

``qidoc`` supports two documentation tools:

* Doxygen
* sphinx

In the following tutorial, you will learn how to configure
``qidoc``, build the documentation and open it.

.. contents:: Table of Contents
    :depth: 2

Configuring qidoc
------------------

Using doxygen
+++++++++++++

Suggested layout:

::

    <worktree>
    |_ libfoo
        |__ qiproject.xml
        |__ foo
        |    |__ foo.h
        |__ foo.dox
        |__ Doxyfile



Here what the files would look like

.. code-block:: xml

  <!-- libfoo/qiproject.xml -->

  <project version="3" >

    <!-- used by qibuild to build your library -->
    <qibuild name="libfoo" />

    <!-- used by qidoc to build the Doxygen documentation -->
    <qidoc name="libfoo-dox" type="doxygen" />

  </project>


::

  # libfoo/dox/Doxfile

  INPUT=. foo/


(No need for ``OUTPUT`` or ``GENERATE_*`` options, they will be set
by ``qidoc`` automatically)



Using sphinx
+++++++++++++

Suggested layout:

::

    <worktree>
    |_ libfoo
        |__ qiproject.xml
        |__ foo
        |    |__ foo.h
        |__ doc
            |_ qiproject.xml
            |_ source
               |_ conf.py
               |_ index.rst


This time you have to tell the ``qiproject.xml`` in ``libfoo`` that there is
a sphinx doc project in the ``doc`` subfolder:

.. code-block:: xml

  <!-- in libfoo/qiproject.xml -->
  <project version="3">

    <qibuild name="libfoo" />
    <project src="doc" />
  </project>

.. code-block:: xml

  <!-- in libfoo/doc/qiproject.xml -->
  <project version="3">
    <qidoc name="libfoo" type="sphinx" />
  </project>


Building documentation
-----------------------

This is done with the ``qidoc build`` command.

As for the ``qibuild`` tool, you can either specify the name
of the doc project, or go to a subdirectory of the documentation project.

For instance, in our ``sphinx`` example:

.. code-block:: console


  cd libfoo/doc
  qidoc build
  # or:
  qidoc build libfoo

The resulting ``html`` files will be found in a ``build-doc`` folder, next
to the ``qiproject.xml`` file.


Browsing the documentation
--------------------------

You can then see the results in your browser by running ``qidoc open``

If you wish to share your documentation and you have
``~/public/html`` directory served by a web server, you can run:

.. code-block:: console

  qidoc install ~/public/html


Adding templates
----------------

Sometimes you want to share configuration across several doc projects.
To do this you can put all the common configuration in a 'template'
project.

Layout is::

  <worktree>
  |_ doc
     |_ templates
     |_ qiproject.xml
     |_ sphinx
     |  |_ conf.in.py
     |  |__ _themes
     |     |_ mytheme
     |        |_ theme.conf
     |        |_ layout.html
     |_ doxygen
     |  |_ Doxyfile.in
     |  |_ doxygen.css
     |  |_ footer.html
     |  |_ header.html
     |_ doc_proj1
     |_ doc_proj2


.. code-block:: xml

  <!-- in doc/templates/qiproject.xml -->
  <project version="3">
    <qidoc type="template" />
  </project>

.. code-block:: python

    # in doc/templates/sphinx/conf.in.py

    master_doc = 'index'
    pygments_style = 'sphinx'
    html_theme = "mytheme"

    extensions = ["custom.extension"]

::

    # in doc/templates/doxygen/Doxyfile.in

    HTML_HEADER = header.html
    HTML_FOOTER = footer.html
    HTML_STYLESHEET = doxygen.css

.. code-block:: python

    # in doc/doc_proj1/source/conf.in.py

    extensions.append("myext")

::

    # in doc/doc_proj2/Doxyfile.in

    INPUT = .



The contents of the ``.in`` files will be concatenated together by ``qidoc build``
That is, a ``conf.py`` file will be generated, containing first the contents of
the file in the template project, then the contents of the file in the doc project.
