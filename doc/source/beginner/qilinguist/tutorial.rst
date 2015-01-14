.. _qilinguist-tutorial:

Translating projects with qilinguist
====================================

``qilinguist`` can be used with ``qt`` or ``gettext``.

In the following tutorial, you will learn how to configure
``qilinguist``, and how to use it to build and install translation
files.

.. contents:: Table of contents
  :depth: 2

Using qilinguist with gettext
-----------------------------


Suggested layout:
+++++++++++++++++

::

  <worktree>
  |__ hello
      |__ qiproject.xml
      |__ po
      |   |__ POTFILES.in
      |__ hello.cpp

.. code-block:: xml

  <!-- qiproject.xml -->
  <project version="3">
    <qilinguist name="hello" linguas="en_US fr_FR" tr="gettext" />
  </project>

.. code-block:: bash

  # po/POTFILES.in

  hello.cpp

.. code-block:: cpp

  // hello.cpp

  #include <libintl.h>
  #define _(string) gettext(string)

  setlocale(LC_ALL, "");
  bindtextdomain("hello", ...);
  textdomain("hello");

  std::cout << _("Hello, world");

* ``po/POTFILES.in`` should list every file that contains strings that should be
  translated.

* The name of the ``qilinguist`` project in the ``qilinguist`` tag in ``qiproject.xml``
  should match the argument of ``bindtextdomain`` and ``textdomain`` calls.


Creating or updating ``.po`` files
+++++++++++++++++++++++++++++++++++

Run ``qilinguist update``

This will create or update the ``.po`` files in
the ``po`` directory, one for each language defined in the
``linguas`` attribute of the ``qilinguist`` tag in the ``qiproject.xml``

Generating the ``.mo`` files
++++++++++++++++++++++++++++

Run ``qilinguist release``.

This will create all the ``.mo`` files from the ``.po`` files.



Using qilinguist with qt linguist
----------------------------------

Suggested layout:
+++++++++++++++++

::

  <worktree>
  |__ hello
      |__ qiproject.xml
      |__ po
      |   |__ POTFILES.in
      |__ hello.cpp

.. code-block:: xml

  <!-- qiproject.xml -->
  <project version="3">
    <qilinguist name="hello" linguas="en_US fr_FR" tr="linguist" />
  </project>

.. code-block:: bash

  # po/POTFILES.in

  hello.cpp

.. code-block:: cpp

  // hello.cpp

  #include <QApplication>
  #include <QTranslator>

  QApplication app;
  QTranslator translator;
  translator.load(..., ...);
  app.installTranslator(&translator);
  QString hello = QApplication::tr("Hello world!");

Updating ``.ts`` files
++++++++++++++++++++++

Run ``qilinguist update``

This will create or update the ``.ts`` files in
the ``po`` directory, one for each language defined in the
``linguas`` attribute of the ``qilinguist`` tag in the ``qiproject.xml``

Creating the ``.qm`` files
+++++++++++++++++++++++++++

Run ``qilinguist release``.

This will create all the ``.qm`` files from the ``.ts`` files.
