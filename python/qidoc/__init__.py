## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" qidoc : handle generating sphinx and doxygen documentation of qibuild
projects



qiDoc: documentation generator
==============================


qiDoc helps you easily write and merge several
documentation formats, doxygen and sphinx for the moment.

Usage:
-----

qidoc is controlled by a simple config file, looking like

.. code-block:: xml

    <qidoc>
      <repo name="qibuild">
        <sphinxdoc name="qibuild" src="doc" />
      </repo>

      <repo name="libnaoqi" >
        <doxydoc name="libalcommon" src="libalcommon/doc" />
        <doxydoc name="libalvision" src="libalvisio/doc" />
      </repo>

      <repo name="doc">
        <sphinxdoc name="doc" src="source" dest="." />
      </repo>

      <defaults>
        <root_project name="doc" />
      </defaults>

      <templates>
        <doxygen
          doxyfile="soure/tools/Doxyfile.template"
          css="soure/tools/doxygen.template.css"
          header="soure/tools/header.template.html"
          footer="soure/tools/footer.template.html"
        />
        <sphinx
          config="source/conf.py"
        />
      </templates>


    </qidoc>


Such a file will produce a documentation looking like

::

  doc/ index.html (doc)
      / libalmotion/index  (doxy libnaoqi/almotion)
      / libalvision/index  (doxy libnaoqi/avisiion)
      / qibuild/index      (sphinx qibuild)


"""
