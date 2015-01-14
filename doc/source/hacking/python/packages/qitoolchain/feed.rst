qitoolchain.feeds -- Parsing toolchain feeds
============================================

.. py:module:: qitoolchain.feed

All the XML parsing is done with the excellent `xml.etree.ElementTree`
standard Python library.

qitoolchain.feed.ToolchainFeedParser
------------------------------------

.. py:class:: ToolchainFeedParser

   A class to handle feed parsing

   .. py:attribute:: packages

      A list of packages, stored as ``ElementTree`` objects.
      The feed where the package came from is stored in a
      "feed" XML attribute of this package for later use.

    .. py:attribute:: _versions

       A dictionary ``name->version`` used to only keep the latest
       version of packages

    .. py:method::  append_package(package_tree)

        Add a package to self.packages.
        If an older version of the package exists,
        replace it by the new version

    .. py:method:: parse(feed)

       Recursively parse the feeds, filling :py:attr:`packages` while doing so.

.. seealso::

  * You can read about the XML format of feeds in the
    :ref:`toolchain-feed-syntax` section.
  * You can read more about what happens next when using
    `qitoolchain create`, `qibuild configure` in the
    :ref:`parsing-toolchain-feeds` overview

