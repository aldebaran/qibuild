.. _qidoc-tutorial:

Building documentation with qidoc
=================================

``qidoc`` supports two documentation tools:

 * doxygen
 * sphinx


Standalone doxygen
------------------


Suggested layout
++++++++++++++++


::

    <worktree>
    |_ libfoo
        |__ qiproject.xml
        |__ foo
             |__ foo.h
        |__ dox
             |__ foo.dox
             |__ Doxyfile
             |__ qiproject.xml



Here what the files would look like

.. code-block:: xml

  <!-- libfoo/qiproject.xml -->

  <project version="3" >
    <!-- used by qibuild to build your library -->
    <qibuild name="libfoo" ../>

    <project src="doc" >
  </project>


.. code-block:: xml

  <!-- libfoo/dox/qiproject.xml -->

  <project version="3" >
    <qidoc name="libfoo-dox" />
  </project>


::

  # libfoo/dox/Doxfile

  INPUT=../..


(No need for ``OUTPUT`` or ``GENERATE_*`` options, they will be set
by ``qidoc`` automatically)


Standalone sphinx
-----------------


